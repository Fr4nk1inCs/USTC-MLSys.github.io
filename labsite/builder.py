from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .content import load_content, sort_blog, sort_news, sort_publications, sort_projects, sort_team
from .render import normalize_base_path, render_site


def build_site(project_root: Path, base_path: str = "/") -> Path:
    content_dir = project_root / "content"
    assets_dir = project_root / "assets"
    dist_dir = project_root / "dist"
    bundle = load_content(content_dir)
    bundle["projects"] = sort_projects(bundle["projects"])
    bundle["blog"] = sort_blog(bundle["blog"])
    bundle["publications"] = sort_publications(bundle["publications"])
    bundle["news"] = sort_news(bundle["news"])
    bundle["team"] = sort_team(bundle["team"])
    base_path = normalize_base_path(base_path)

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(assets_dir, dist_dir / "assets", dirs_exist_ok=True)
    copy_extra_static_dirs(project_root, dist_dir)

    rendered_pages = render_site(bundle, base_path)
    for page in rendered_pages:
        output_path = dist_dir / page.path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            SiteHtmlWrapper(bundle, base_path).wrap(page),
            encoding="utf-8",
        )

    write_search_index(dist_dir, bundle, base_path)
    write_manifest(dist_dir, bundle["site"], base_path)
    write_robots(dist_dir, bundle["site"], base_path)
    write_nojekyll(dist_dir)
    write_sitemap(dist_dir, bundle["site"], base_path, rendered_pages)
    return dist_dir


class SiteHtmlWrapper:
    def __init__(self, bundle: dict[str, Any], base_path: str) -> None:
        self.bundle = bundle
        self.base_path = base_path

    def wrap(self, page: Any) -> str:
        from .render import SiteRenderer

        return SiteRenderer(self.bundle, self.base_path).page_shell(
            title=page.title,
            description=page.description,
            current_section=page.current_section,
            page_kind=page.page_kind,
            body=page.content,
        )


def copy_extra_static_dirs(project_root: Path, dist_dir: Path) -> None:
    for path in project_root.iterdir():
        # Support two patterns for blog assets:
        # 1) top-level folders named `blog-<name>` (legacy)
        # 2) a `blog/` folder containing subfolders per blog (e.g. `blog/TWIST`)
        if path.is_dir() and path.name.startswith("blog-"):
            # Convert top-level `blog-<name>` dirs into `dist/blog/<name>/`
            parts = path.name.split("-", 1)
            if len(parts) == 2 and parts[1]:
                target = dist_dir / "blog" / parts[1]
            else:
                target = dist_dir / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(path, target, dirs_exist_ok=True)
        elif path.is_dir() and path.name == "blog":
            # Copy nested blog/<name>/ folders into dist/blog/<name>/
            for sub in path.iterdir():
                if not sub.is_dir():
                    continue
                target = dist_dir / "blog" / sub.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(sub, target, dirs_exist_ok=True)


def write_search_index(dist_dir: Path, bundle: dict[str, Any], base_path: str) -> None:
    items: list[dict[str, Any]] = []
    for project in bundle["projects"]:
        prefix = f"{base_path}projects/" if base_path != "/" else "/projects/"
        items.append(
            {
                "type": "project",
                "title": project["title"],
                "url": f"{prefix}{project['slug']}/",
                "summary": project["summary"],
                "tags": project.get("tags", []),
            }
        )
    for post in bundle["blog"]:
        prefix = f"{base_path}blog/" if base_path != "/" else "/blog/"
        items.append(
            {
                "type": "blog",
                "title": post["title"],
                "url": f"{prefix}{post['slug']}/",
                "summary": post["summary"],
                "tags": post.get("tags", []),
            }
        )
    for pub in bundle["publications"]:
        items.append(
            {
                "type": "publication",
                "title": pub["title"],
                "url": f"{base_path}publications/{pub['slug']}/" if base_path != "/" else f"/publications/{pub['slug']}/",
                "summary": pub["summary"],
                "tags": pub.get("tags", []),
            }
        )
    (dist_dir / "search-index.json").write_text(json.dumps(items, indent=2), encoding="utf-8")


def write_manifest(dist_dir: Path, site: dict[str, Any], base_path: str) -> None:
    manifest = {
        "name": site["lab_name"],
        "short_name": site["short_name"],
        "start_url": base_path,
        "display": "standalone",
        "background_color": "#f4f1ea",
        "theme_color": "#121417",
        "icons": [
            {
                "src": f"{base_path}assets/img/favicon.svg" if base_path != "/" else "/assets/img/favicon.svg",
                "sizes": "120x120",
                "type": "image/svg+xml",
            }
        ],
    }
    (dist_dir / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_robots(dist_dir: Path, site: dict[str, Any], base_path: str) -> None:
    lines = ["User-agent: *", "Allow: /"]
    base_url = site.get("base_url", "").rstrip("/")
    if base_url:
        lines.append(f"Sitemap: {base_url}{base_path}sitemap.xml")
    (dist_dir / "robots.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_sitemap(dist_dir: Path, site: dict[str, Any], base_path: str, pages: list[Any]) -> None:
    base_url = site.get("base_url", "").rstrip("/")
    if not base_url:
        return
    page_urls = []
    base_prefix = f"{base_url}{base_path.rstrip('/')}"
    for page in pages:
        if page.path == "404.html":
            continue
        page_path = "" if page.path == "index.html" else page.path.replace("index.html", "")
        page_urls.append(f"{base_prefix}/{page_path}".replace("//", "/").replace("https:/", "https://"))
    entries = "\n".join(f"  <url><loc>{url}</loc></url>" for url in page_urls)
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""
    (dist_dir / "sitemap.xml").write_text(sitemap, encoding="utf-8")


def write_nojekyll(dist_dir: Path) -> None:
    (dist_dir / ".nojekyll").write_text("", encoding="utf-8")
