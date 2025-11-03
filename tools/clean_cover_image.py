#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量清理 content/ 下所有 Markdown 的 Front Matter 中空的 cover_image_url。

规则：
- 仅处理文首首个 `---` 到下一个 `---` 的 Front Matter。
- 若存在形如：
    cover_image_url:
    cover_image_url: ""
    cover_image_url: ''
    cover_image_url: null
  则删除该行。

运行：
  python tools/clean_cover_image.py
"""

from __future__ import annotations

import sys
from pathlib import Path


def is_markdown(path: Path) -> bool:
    return path.suffix.lower() in {".md", ".markdown"}


def clean_file(path: Path) -> bool:
    """清理单个文件，返回是否发生修改。"""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False

    # 定位 front matter 边界
    try:
        end_idx = text.find("\n---", 3)
        if end_idx == -1:
            return False
        end_idx += 4  # 指向第二个 --- 末尾
    except Exception:
        return False

    fm = text[0:end_idx]
    body = text[end_idx:]

    # 逐行过滤 cover_image_url 为空值的行
    lines = fm.splitlines()
    out_lines = []
    modified = False
    for i, line in enumerate(lines):
        if i == 0 or i == len(lines) - 1:  # 保留开闭合 ---
            out_lines.append(line)
            continue
        stripped = line.strip()
        if stripped.lower().startswith("cover_image_url:"):
            # 获取冒号后的值
            value = stripped.split(":", 1)[1].strip()
            if value in ("", "''", '""', "null", "~"):
                modified = True
                continue  # 跳过该行
        out_lines.append(line)

    if not modified:
        return False

    new_text = "\n".join(out_lines) + body
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    content_dir = base_dir / "content"
    if not content_dir.is_dir():
        print("content 目录不存在")
        return 1

    changed = 0
    total = 0
    for p in content_dir.rglob("*"):
        if p.is_file() and is_markdown(p):
            total += 1
            try:
                if clean_file(p):
                    changed += 1
                    print(f"✔ 修改: {p.relative_to(base_dir)}")
            except Exception as e:
                print(f"✖ 失败: {p} -> {e}")

    print(f"完成：共检查 {total} 个 Markdown，修改 {changed} 个。")
    return 0


if __name__ == "__main__":
    sys.exit(main())


