from __future__ import annotations

import argparse
from pathlib import Path

from labsite.builder import build_site


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the static website into dist/.")
    parser.add_argument(
        "--base-path",
        default="/",
        help="Base path for GitHub Pages. Use / for root or /repo-name/ for project pages.",
    )
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parent
    dist_dir = build_site(project_root, base_path=args.base_path)
    print(f"Built site into {dist_dir}")


if __name__ == "__main__":
    main()
