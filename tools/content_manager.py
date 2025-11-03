#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory


BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / 'content'

app = Flask(__name__, static_folder='static')


def _parse_date_from_filename(p: Path):
    # 期望格式: YYYY-MM-DD-xxxx.md
    try:
        base = p.stem
        parts = base.split('-')
        if len(parts) >= 3:
            yyyy, mm, dd = parts[0], parts[1], parts[2]
            if len(yyyy) == 4 and len(mm) == 2 and len(dd) == 2:
                return int(yyyy), int(mm), int(dd)
    except Exception:
        return None
    return None


def _build_tree_filtered(root: Path):
    """返回 (node, has_markdown)；没有 markdown 时返回 (None, False)。"""
    node = {
        'name': root.name,
        'path': str(root.relative_to(BASE_DIR)),
        'type': 'directory',
        'children': []
    }
    has_md = False
    try:
        dirs = []
        files = []
        for entry in root.iterdir():
            if entry.name.startswith('.'):
                continue
            if entry.is_dir():
                dirs.append(entry)
            elif entry.suffix.lower() in {'.md', '.markdown'}:
                files.append(entry)

        # 目录按名称降序（例如年份 2025 > 2024）
        dirs.sort(key=lambda d: d.name.lower(), reverse=True)

        # 文件按日期降序；若无法解析日期则按修改时间降序
        def file_sort_key(f: Path):
            date_tuple = _parse_date_from_filename(f)
            if date_tuple is not None:
                return (date_tuple[0], date_tuple[1], date_tuple[2], f.name.lower())
            return (0, 0, 0, f.stat().st_mtime)

        files.sort(key=file_sort_key, reverse=True)

        for d in dirs:
            child_node, child_has_md = _build_tree_filtered(d)
            if child_has_md:
                node['children'].append(child_node)
                has_md = True

        def read_front_datetime(p: Path):
            try:
                with p.open('r', encoding='utf-8') as fp:
                    head = fp.read(2048)
                if not head.startswith('---'):
                    return None
                # 仅取 front matter 区域
                end = head.find('\n---', 3)
                block = head[: end + 4] if end != -1 else head
                for line in block.splitlines():
                    if line.strip().lower().startswith('datetime:'):
                        return line.split(':', 1)[1].strip()
                return None
            except Exception:
                return None

        for f in files:
            node['children'].append({
                'name': f.name,
                'path': str(f.relative_to(BASE_DIR)),
                'type': 'file',
                'datetime': read_front_datetime(f)
            })
            has_md = True
    except Exception:
        pass
    if not has_md:
        return None, False
    return node, True


def build_tree(root: Path):
    # 根节点始终存在，但其 children 过滤无 Markdown 的分支
    node, has_md = _build_tree_filtered(root)
    if node is None:
        return {
            'name': root.name,
            'path': str(root.relative_to(BASE_DIR)),
            'type': 'directory',
            'children': []
        }
    return node


@app.route('/')
def index():
    return send_from_directory((Path(__file__).parent / 'static'), 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory((Path(__file__).parent / 'static'), filename)


@app.route('/assets/<path:filename>')
def assets_files(filename):
    """为编辑器预览提供图片等静态资源。

    优先从内容目录下的 assets 提供（content/assets），
    若不存在则回退到项目根目录的 assets。
    """
    content_assets = BASE_DIR / 'content' / 'assets'
    root_assets = BASE_DIR / 'assets'
    # 优先 content/assets
    candidate = content_assets / filename
    if candidate.exists() and candidate.is_file():
        return send_from_directory(content_assets, filename)
    # 回退根目录 assets
    candidate = root_assets / filename
    if candidate.exists() and candidate.is_file():
        return send_from_directory(root_assets, filename)
    return jsonify({'error': 'asset not found'}), 404


@app.route('/api/tree')
def api_tree():
    return jsonify(build_tree(CONTENT_DIR))


@app.route('/api/file')
def api_get_file():
    rel_path = request.args.get('path', '')
    if not rel_path:
        return jsonify({'error': 'path required'}), 400
    abs_path = (BASE_DIR / rel_path).resolve()
    if not abs_path.is_file() or not abs_path.is_relative_to(CONTENT_DIR):
        return jsonify({'error': 'invalid path'}), 400
    text = abs_path.read_text(encoding='utf-8')
    return jsonify({'path': rel_path, 'content': text})


@app.route('/api/save', methods=['POST'])
def api_save_file():
    data = request.get_json(force=True)
    rel_path = data.get('path', '')
    content = data.get('content', '')
    if not rel_path:
        return jsonify({'error': 'path required'}), 400
    abs_path = (BASE_DIR / rel_path).resolve()
    if not abs_path.parent.is_relative_to(CONTENT_DIR):
        return jsonify({'error': 'invalid path'}), 400
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(content, encoding='utf-8')
    return jsonify({'ok': True})


@app.route('/api/delete', methods=['POST'])
def api_delete_file():
    data = request.get_json(force=True)
    rel_path = (data.get('path') or '').strip()
    if not rel_path:
        return jsonify({'error': 'path required'}), 400
    abs_path = (BASE_DIR / rel_path).resolve()
    try:
        if not abs_path.is_file() or not abs_path.parent.is_relative_to(CONTENT_DIR):
            return jsonify({'error': 'invalid path'}), 400
        abs_path.unlink(missing_ok=False)
        return jsonify({'ok': True})
    except FileNotFoundError:
        return jsonify({'error': 'not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/push', methods=['POST'])
def api_push():
    """执行 git add/commit/push，并返回合并日志。

    提交信息：push-<timestamp_ms>
    在仓库根目录 BASE_DIR 下执行。
    """
    import time
    import subprocess

    def run(cmd):
        try:
            p = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
            out = (p.stdout or '') + (p.stderr or '')
            return p.returncode, out
        except Exception as e:
            return 1, f"Command failed: {' '.join(cmd)}\n{e}\n"

    ts = int(time.time() * 1000)
    logs = []

    steps = [
        ["git", "status"],
        ["git", "add", "-A"],
        ["git", "commit", "-m", f"push-{ts}", "--allow-empty"],
        ["git", "push"],
    ]
    ok = True
    for cmd in steps:
        code, out = run(cmd)
        logs.append(f"$ {' '.join(cmd)}\n{out}\n")
        if code != 0 and cmd[0:2] != ["git", "commit"]:  # 允许 allow-empty 导致的非变更提交通过
            ok = False
            break

    return jsonify({
        'ok': ok,
        'log': "\n".join(logs)
    })

@app.route('/api/upload_image', methods=['POST'])
def api_upload_image():
    """接受粘贴/上传的图片，保存到 content/assets/{year}/ 下。

    请求：multipart/form-data
      - image: 文件
      - year: 可选，数字年份；缺省则用当前年份
    返回：{ url: "/assets/{year}/{filename}" }
    """
    import time
    import mimetypes

    if 'image' not in request.files:
        return jsonify({'error': 'image required'}), 400
    f = request.files['image']
    try:
        y = request.form.get('year')
        year = int(y) if y else datetime.datetime.now().year
    except Exception:
        year = datetime.datetime.now().year

    # 计算扩展名
    ext = ''
    if f.mimetype:
        guessed = mimetypes.guess_extension(f.mimetype) or ''
        ext = (guessed or '').lower()
        # 有些 mimetype 会映射为 .jpe，统一成 .jpg
        if ext in {'.jpe'}:
            ext = '.jpg'
    if not ext:
        # 尝试从原始文件名获取
        orig = (f.filename or '').lower()
        for cand in ('.png', '.jpg', '.jpeg', '.gif', '.webp'):
            if orig.endswith(cand):
                ext = cand if cand != '.jpeg' else '.jpg'
                break
    if not ext:
        ext = '.png'

    ts_ms = int(time.time() * 1000)
    filename = f"{ts_ms}{ext}"
    target_dir = CONTENT_DIR / 'assets' / str(year)
    target_dir.mkdir(parents=True, exist_ok=True)
    save_path = target_dir / filename
    f.save(save_path)

    url = f"/assets/{year}/{filename}"
    rel_path = str(save_path.relative_to(BASE_DIR))
    return jsonify({'ok': True, 'url': url, 'path': rel_path})

@app.route('/api/rename', methods=['POST'])
def api_rename_file():
    data = request.get_json(force=True)
    rel_path = (data.get('path') or '').strip()
    new_name = (data.get('new_name') or '').strip()
    if not rel_path or not new_name:
        return jsonify({'error': 'path and new_name required'}), 400
    src = (BASE_DIR / rel_path).resolve()
    if not src.is_file() or not src.parent.is_relative_to(CONTENT_DIR):
        return jsonify({'error': 'invalid path'}), 400
    # 仅允许更改同一目录下的文件名
    dst = (src.parent / new_name).resolve()
    if not dst.parent == src.parent:
        return jsonify({'error': 'rename must stay in same directory'}), 400
    try:
        src.rename(dst)
        rel = str(dst.relative_to(BASE_DIR))
        return jsonify({'ok': True, 'path': rel})
    except FileExistsError:
        return jsonify({'error': 'target exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/new', methods=['POST'])
def api_new_file():
    data = request.get_json(force=True)
    title = (data.get('title') or '').strip()
    tags = (data.get('tags') or '').strip()
    summary = (data.get('summary') or '').strip()
    year_override = data.get('year')  # 可选：指定年份目录
    now = datetime.datetime.now()
    try:
        target_year = int(year_override) if year_override is not None else now.year
    except Exception:
        target_year = now.year
    year_dir = CONTENT_DIR / f'{target_year}'
    year_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名：有标题则直接用标题；无标题则用当前时间
    if title:
        safe_name = ''.join(c for c in title if c not in '\\/:*?"<>|').strip()
        filename = f"{safe_name}.md" if safe_name else f"{now.strftime('%Y-%m-%d-%H%M%S')}.md"
    else:
        safe_name = ''
        filename = f"{now.strftime('%Y-%m-%d-%H%M%S')}.md"
    target = year_dir / filename
    i = 1
    while target.exists():
        target = year_dir / f"{target.stem}-{i}.md"
        i += 1

    front_matter = [
        '---',
        '',
        f'title: {title or target.stem}',
        f'slug: {target.stem}',
        f'datetime: {now.strftime("%Y-%m-%d %H:%M")}',
        f'date: {now.strftime("%Y-%m-%d %H:%M")}',
        f'summary: {summary}',
        f'tags: {tags}',
        '',
        '---',
        '',
        ''
    ]
    target.write_text('\n'.join(front_matter), encoding='utf-8')

    rel = str(target.relative_to(BASE_DIR))
    return jsonify({'ok': True, 'path': rel})


@app.route('/api/search', methods=['POST'])
def api_search():
    """简单全文检索：在 content/ 下查找包含关键词的 Markdown。

    请求 JSON: { q: string, limit?: int }
    返回: { results: [{ path, title, snippet }] }
    """
    data = request.get_json(force=True)
    q = (data.get('q') or '').strip()
    limit = int(data.get('limit') or 50)
    if not q:
        return jsonify({'results': []})

    q_lower = q.lower()
    results = []

    def get_title_and_snippet(p: Path) -> tuple[str, str]:
        title = p.stem
        snippet = ''
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return title, snippet
        # 读取 title
        if text.startswith('---'):
            end = text.find('\n---', 3)
            block = text[: end + 4] if end != -1 else text
            for line in block.splitlines():
                if line.strip().lower().startswith('title:'):
                    t = line.split(':', 1)[1].strip()
                    if t:
                        title = t
                    break
        # 查找片段
        idx = text.lower().find(q_lower)
        if idx != -1:
            start = max(0, idx - 40)
            end = min(len(text), idx + 80)
            snippet = text[start:end].replace('\n', ' ')
        return title, snippet

    for p in CONTENT_DIR.rglob('*.md'):
        if len(results) >= limit:
            break
        try:
            # 文件名匹配或内容匹配
            hit = q_lower in p.name.lower()
            title, snippet = get_title_and_snippet(p)
            hit = hit or (q_lower in title.lower()) or (q_lower in snippet.lower())
            if hit:
                results.append({
                    'path': str(p.relative_to(BASE_DIR)),
                    'title': title,
                    'snippet': snippet
                })
        except Exception:
            continue

    return jsonify({'results': results})

def main():
    import argparse
    parser = argparse.ArgumentParser(description='内容管理工具（目录树 + Markdown 编辑器）')
    parser.add_argument('-p', '--port', type=int, default=5000, help='端口（默认 5000）')
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=True)


if __name__ == '__main__':
    main()


