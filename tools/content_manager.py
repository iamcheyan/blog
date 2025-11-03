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

        for f in files:
            node['children'].append({
                'name': f.name,
                'path': str(f.relative_to(BASE_DIR)),
                'type': 'file'
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

    # 生成安全文件名
    base_name = title or now.strftime('%Y-%m-%d-未命名')
    safe_name = ''.join(c for c in base_name if c not in '\\/:*?"<>|').strip()
    # 文件名前缀：指定年份 + 当天月日
    date_prefix = f"{target_year}-{now.month:02d}-{now.day:02d}"
    filename = f"{date_prefix}-{safe_name}.md"
    target = year_dir / filename
    i = 1
    while target.exists():
        target = year_dir / f"{now.strftime('%Y-%m-%d')}-{safe_name}-{i}.md"
        i += 1

    front_matter = [
        '---',
        f'title: {title or "新文章"}',
        f'slug: {target.stem}',
        f'datetime: {date_prefix} {now.strftime("%H:%M")}',
        f'date: {date_prefix} {now.strftime("%H:%M")}',
        f'summary: {summary}',
        f'tags: {tags}',
        'cover_image_url: ',
        '---',
        '',
        '正文内容...',
        ''
    ]
    target.write_text('\n'.join(front_matter), encoding='utf-8')

    rel = str(target.relative_to(BASE_DIR))
    return jsonify({'ok': True, 'path': rel})


def main():
    import argparse
    parser = argparse.ArgumentParser(description='内容管理工具（目录树 + Markdown 编辑器）')
    parser.add_argument('-p', '--port', type=int, default=5000, help='端口（默认 5000）')
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=True)


if __name__ == '__main__':
    main()


