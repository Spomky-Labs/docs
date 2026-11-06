#!/usr/bin/env python3
"""Build the whole site: the hub at the root, one directory per project and per version.

    python3 -I tools/build.py [--strict] [--only <prefix>] [--output site]
    python3 -I tools/build.py --sync-shared

    site/                     the hub
    site/jwt/4.3/             a version, built from projects/jwt/4.3/
    site/jwt/latest/          a copy of the newest version
    site/jwt/versions.json    what the version selector of that project reads
    site/jwt/index.html       sends /jwt/ to /jwt/latest/

Every project holds its own pages, its project mark and its logo partial. Everything else — the fonts,
the stylesheets, the shared brand files and the three common templates — lives once in shared/ and is
copied in before each build. Those copies are in .gitignore: they are not sources.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared"


def version_key(version: str):
    """1.10 after 1.9, and 11.6 after 4.3."""
    return [int(p) if p.isdigit() else p for p in re.split(r"[.-]", version)]


def copy_shared(project: Path) -> None:
    for source in sorted((SHARED / "assets").rglob("*")):
        if source.is_file():
            target = project / "docs" / "assets" / source.relative_to(SHARED / "assets")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    for source in sorted((SHARED / "overrides").rglob("*")):
        if source.is_file():
            target = project / "overrides" / source.relative_to(SHARED / "overrides")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


def mkdocs(config: Path, out: Path, strict: bool) -> None:
    command = [sys.executable, "-m", "mkdocs", "build", "-f", str(config), "-d", str(out)]
    if strict:
        command.append("--strict")
    subprocess.run(command, check=True, cwd=ROOT)


REDIRECT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Redirecting</title>
<link rel="canonical" href="latest/">
<meta http-equiv="refresh" content="0; url=latest/">
<script>location.replace("latest/" + location.search + location.hash);</script>
</head>
<body><a href="latest/">Redirecting to the latest version…</a></body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--only", default=None, help="one project prefix")
    parser.add_argument("--output", default="site")
    parser.add_argument("--sync-shared", action="store_true",
                        help="copy shared/ into the hub and every project, and stop there")
    args = parser.parse_args()

    if args.sync_shared:
        copy_shared(ROOT)
        for config in sorted(ROOT.glob("projects/*/*/mkdocs.yml")):
            copy_shared(config.parent)
        print("shared/ copied into the hub and every project")
        return 0

    out = (ROOT / args.output).resolve()
    if out.exists():
        shutil.rmtree(out)

    # The hub owns the root, so it is built first: a project writes only its own directory afterwards.
    print("hub")
    copy_shared(ROOT)
    mkdocs(ROOT / "mkdocs.yml", out, args.strict)

    projects: dict[str, list[str]] = {}
    for config in sorted(ROOT.glob("projects/*/*/mkdocs.yml")):
        projects.setdefault(config.parts[-3], []).append(config.parts[-2])

    for prefix, versions in sorted(projects.items()):
        if args.only and prefix != args.only:
            continue
        versions.sort(key=version_key, reverse=True)
        for version in versions:
            project = ROOT / "projects" / prefix / version
            copy_shared(project)
            print(f"{prefix}/{version}")
            mkdocs(project / "mkdocs.yml", out / prefix / version, args.strict)

        # "latest" is a copy of the newest version, as mike makes it: every page keeps the canonical
        # address of the version it belongs to.
        newest = versions[0]
        shutil.copytree(out / prefix / newest, out / prefix / "latest")

        (out / prefix / "versions.json").write_text(json.dumps(
            [{"version": v, "title": v, "aliases": ["latest"] if v == newest else []} for v in versions],
            indent=2) + "\n", encoding="utf-8")
        (out / prefix / "index.html").write_text(REDIRECT, encoding="utf-8")
        print(f"{prefix}: {', '.join(versions)} — latest is {newest}")

    for source in sorted((ROOT / "site-root").rglob("*")):
        if source.is_file():
            target = out / source.relative_to(ROOT / "site-root")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    (out / ".nojekyll").touch()

    pages = sum(1 for _ in out.rglob("index.html"))
    print(f"\n{out}: {pages} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
