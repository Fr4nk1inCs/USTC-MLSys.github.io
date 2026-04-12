#!/usr/bin/env python3
"""
Replace "publication" → "publication" across the repo while preserving publication titles/descriptions.
- JSON files: parse and avoid replacing inside keys named in BANNED_KEYS (title, summary, description, abstract, note, explanation, name)
- Markdown files: skip frontmatter block (--- ... ---) from replacement to preserve titles/description there
- Other text files: apply replacements
- Renames files/dirs containing 'publication' -> 'publication'

Usage:
  python tools\replace_paper.py --preview   # only show diffs
  python tools\replace_paper.py --apply     # apply edits and renames

Always run in a git-clean working tree so you can roll back.
"""

from pathlib import Path
import os
import sys
import re
import json
import difflib
from typing import Any

ROOT = Path('.').resolve()
EXCLUDE_DIRS = {'.git', 'dist', 'node_modules', '.venv', '__pycache__'}
BANNED_KEYS = {'title', 'name', 'summary', 'description', 'abstract', 'note', 'explanation'}

REPLACEMENTS = [
    (re.compile(r"\bPapers\b"), 'Publications'),
    (re.compile(r"\bpapers\b"), 'publications'),
    (re.compile(r"\bPaper\b"), 'Publication'),
    (re.compile(r"\bpaper\b"), 'publication'),
]

TEXT_EXTS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.css', '.scss', '.html', '.htm', '.txt', '.md', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.json'}


def transform_text(text: str) -> str:
    out = text
    for pat, repl in REPLACEMENTS:
        out = pat.sub(repl, out)
    return out


def should_skip_path(p: Path) -> bool:
    try:
        parts = set(p.resolve().parts)
    except Exception:
        parts = set(p.parts)
    return bool(parts & EXCLUDE_DIRS)


def json_replace(obj: Any, key_path=()):
    changed = False
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            # decide new key name (but do not rename banned keys)
            if k.lower() in BANNED_KEYS:
                new_key = k
            else:
                new_key = transform_text(k)
            sub_changed, new_v = json_replace(v, key_path + (k,))
            new_obj[new_key] = new_v
            if new_key != k:
                changed = True
            if sub_changed:
                changed = True
        return changed, new_obj
    elif isinstance(obj, list):
        new_list = []
        for i, item in enumerate(obj):
            sub_changed, new_item = json_replace(item, key_path)
            new_list.append(new_item)
            if sub_changed:
                changed = True
        return changed, new_list
    elif isinstance(obj, str):
        # if any key in path is banned, skip replacement for this string
        if any(k.lower() in BANNED_KEYS for k in key_path):
            return False, obj
        new_s = transform_text(obj)
        if new_s != obj:
            return True, new_s
        return False, obj
    else:
        return False, obj


def process_json_file(path: Path, apply: bool = False):
    try:
        text = path.read_text(encoding='utf-8')
        data = json.loads(text)
    except Exception:
        return []
    changed, new_data = json_replace(data)
    if not changed:
        return []
    new_text = json.dumps(new_data, ensure_ascii=False, indent=2) + '\n'
    if apply:
        path.write_text(new_text, encoding='utf-8')
    return list(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(path), tofile=str(path) + ' (new)', lineterm=''))


def process_markdown_file(path: Path, apply: bool = False):
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return []
    # split frontmatter if present
    fm_match = re.match(r'^(---\n.*?\n---\n)([\s\S]*)$', text, re.DOTALL)
    if fm_match:
        front, body = fm_match.group(1), fm_match.group(2)
        new_body = transform_text(body)
        new_text = front + new_body
    else:
        new_text = transform_text(text)
    if new_text == text:
        return []
    if apply:
        path.write_text(new_text, encoding='utf-8')
    return list(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(path), tofile=str(path) + ' (new)', lineterm=''))


def process_generic_text_file(path: Path, apply: bool = False):
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return []
    new_text = transform_text(text)
    if new_text == text:
        return []
    if apply:
        path.write_text(new_text, encoding='utf-8')
    return list(difflib.unified_diff(text.splitlines(keepends=True), new_text.splitlines(keepends=True), fromfile=str(path), tofile=str(path) + ' (new)', lineterm=''))


def rename_path(path: Path, apply: bool = False):
    name = path.name
    new_name = name
    for pat, repl in REPLACEMENTS:
        new_name = pat.sub(repl, new_name)
    if new_name != name:
        new_path = path.with_name(new_name)
        if apply:
            path.rename(new_path)
        return f"{path} -> {new_path}"
    return None


def walk_repo(apply: bool = False):
    diffs = []
    renames = []
    # process files
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            if should_skip_path(fpath):
                continue
            ext = fpath.suffix.lower()
            if ext == '.json':
                d = process_json_file(fpath, apply=apply)
            elif ext == '.md' or ext == '.markdown':
                d = process_markdown_file(fpath, apply=apply)
            elif ext in TEXT_EXTS:
                d = process_generic_text_file(fpath, apply=apply)
            else:
                d = []
            if d:
                diffs.append((fpath, d))
    # rename files
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            if should_skip_path(fpath):
                continue
            r = rename_path(fpath, apply=apply)
            if r:
                renames.append(r)
    # rename dirs bottom-up
    for root, dirs, files in os.walk(ROOT, topdown=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for d in dirs:
            dpath = Path(root) / d
            if should_skip_path(dpath):
                continue
            r = rename_path(dpath, apply=apply)
            if r:
                renames.append(r)
    return diffs, renames


def print_summary(diffs, renames, apply=False):
    if not diffs and not renames:
        print('No matches found.')
        return
    if diffs:
        print('\n=== File changes preview ===\n')
        for path, diff in diffs:
            print(''.join(diff[:400]))
            print('... (truncated)\n')
    if renames:
        print('\n=== Renames ===\n')
        for r in renames:
            print(r)
    if not apply:
        print('\nTo apply these changes run with --apply')
    else:
        print('\nApplied. Please review, build, and commit changes.')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--preview', action='store_true', help='Alias for preview (no changes)')
    args = parser.parse_args()
    # determine mode: --apply overrides --preview
    apply_mode = bool(args.apply)
    if apply_mode:
        print('APPLY mode: changes and renames will be performed')
    else:
        print('PREVIEW mode: no files will be modified')
    diffs, renames = walk_repo(apply=apply_mode)
    print_summary(diffs, renames, apply=apply_mode)

if __name__ == '__main__':
    main()
