#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批处理：去掉 content/2025/ 下 Markdown 文件名与 Front Matter title 中的日期前缀。

规则：
- 重命名文件：形如 `YYYY-MM-DD-xxxx.md` -> `xxxx.md`
- 修改 Front Matter `title:`：若值以 `YYYY-MM-DD-` 开头则去掉该前缀。
- 仅处理 2025 目录；冲突时在新文件名后追加数字后缀避免覆盖。

运行：
  python tools/strip_date_2025.py
"""

from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TARGET_DIR = BASE / "content" / "2025"

DATE_PREFIX_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")


def strip_date_prefix(text: str) -> str:
    m = DATE_PREFIX_RE.match(text)
    if not m:
        return text
    return text[m.end():]


def process_file(path: Path) -> tuple[bool, str]:
    """处理单个文件。返回 (changed, new_path_str)。"""
    changed = False
    content = path.read_text(encoding="utf-8")

    # 修改 title
    if content.startswith("---"):
        try:
            end = content.find("\n---", 3)
            if end != -1:
                head = content[: end + 4]
                body = content[end + 4 :]
                lines = head.splitlines()
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith("title:"):
                        prefix, val = line.split(":", 1)
                        new_val = strip_date_prefix(val.strip())
                        if new_val != val.strip():
                            lines[i] = f"{prefix}: {new_val}"
                            changed = True
                        break
                head = "\n".join(lines)
                content = head + body
        except Exception:
            pass

    # 计算新文件名
    new_name = strip_date_prefix(path.stem) + path.suffix
    new_path = path.with_name(new_name)
    if new_path != path:
        # 避免重名
        if new_path.exists():
            base = new_path.stem
            n = 1
            while True:
                candidate = new_path.with_name(f"{base}-{n}{new_path.suffix}")
                if not candidate.exists():
                    new_path = candidate
                    break
                n += 1
        changed = True

    if changed:
        # 先写回内容（即使不改名也会覆盖）
        path.write_text(content, encoding="utf-8")
        if new_path != path:
            path.rename(new_path)
        return True, str(new_path.relative_to(BASE))
    return False, str(path.relative_to(BASE))


def main() -> int:
    if not TARGET_DIR.is_dir():
        print("未找到目录:", TARGET_DIR)
        return 1
    changed = 0
    total = 0
    for p in sorted(TARGET_DIR.glob("*.md")):
        total += 1
        try:
            ch, newp = process_file(p)
            if ch:
                changed += 1
                print("✔ 修改:", newp)
        except Exception as e:
            print("✖ 失败:", p, "->", e)
    print(f"完成：检查 {total} 个文件，修改 {changed} 个。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


