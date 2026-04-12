from __future__ import annotations

import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from labsite.builder import build_site


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and preview the static site locally.")
    parser.add_argument("--port", type=int, default=8000, help="Port for the local preview server.")
    parser.add_argument(
        "--base-path",
        default="/",
        help="Base path for the build. Keep / for local preview and pass /repo-name/ when testing project-page links.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent
    dist_dir = build_site(project_root, base_path=args.base_path)
    handler = partial(SimpleHTTPRequestHandler, directory=str(dist_dir))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Serving {dist_dir} at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
