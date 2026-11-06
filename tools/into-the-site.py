#!/usr/bin/env python3
"""Move a documentation into https://docs.spomky-labs.com/, under its own directory.

    python3 -I tools/into-the-site.py <repository> <prefix>

The repository keeps its branches, one per version, and deploys into the gh-pages of Spomky-Labs/docs
under <prefix> instead of publishing a site of its own. The script makes the six edits CONSOLIDATING.md
describes, on the branch that is checked out:

    mkdocs.yml                  site_url, and exclude_docs for the templates of the theme
    docs/overrides/main.html    the share image, whose URL was missing a slash
    .github/workflows/pages.yml the publication, rewritten for the site
    site-root/                  removed: the domain goes with it
    README.md                   the new address, its table, and the token

It is idempotent: a second run on the same branch changes nothing and says so. It writes nothing outside
the repository it is given, commits nothing, and prints what a human still has to look at.
"""

import re
import subprocess
import sys
from pathlib import Path

SITE = "https://docs.spomky-labs.com/"

WORKFLOW = '''name: Pages

# This documentation is one directory of https://docs.spomky-labs.com/, deployed by mike into the gh-pages
# branch of Spomky-Labs/docs under the prefix "{prefix}". One version of the directory per branch: a branch
# named N.M.x is served at /{prefix}/N.M/, and the alias "latest" follows the highest version, which
# /{prefix}/ redirects to. A branch is named N.M, or N.M.x like the maintenance branches of the library;
# N.x is the next minor.
#
# That repository holds the hub at the root of the branch and one directory per project. It publishes the
# root without touching the directories, and this workflow writes nothing but its own.
on:
    push:
        branches:
            - '[0-9]*.[0-9]*'
            - '[0-9]*.x'
        paths-ignore:
            - '.github/workflows/check.yml'
    workflow_dispatch:

# MkDocs 2.0 is announced as backward incompatible with every plugin and theme, so the toolchain is pinned
# to the 1.x line in requirements.txt and the two notices about it are silenced: they are news about the
# ecosystem, not findings about this site.
env:
    NO_MKDOCS_2_WARNING: 'true'
    DISABLE_MKDOCS_2_WARNING: 'true'
    # The directory of this project in the site.
    PREFIX: {prefix}
    SITE_REPOSITORY: Spomky-Labs/docs

permissions:
    contents: read

# Two branches pushed at once must not write the site at the same time, and a queued run is never
# cancelled: it carries a version the other does not.
concurrency:
    group: site-pages
    cancel-in-progress: false

jobs:
    deploy:
        name: Deploy ${{{{ github.ref_name }}}}
        runs-on: ubuntu-latest
        steps:
            # actions/checkout writes the GITHUB_TOKEN of this repository into
            # http.https://github.com/.extraheader, which applies to every github.com URL and takes
            # precedence over the credentials in the URL of a remote: the push to the site would go out as
            # github-actions[bot] and be refused. This repository is public, so nothing here needs those
            # credentials afterwards.
            - uses: actions/checkout@v5
              with:
                  fetch-depth: 0
                  persist-credentials: false

            - uses: actions/setup-python@v6
              with:
                  python-version: '3.13'
                  cache: pip
                  cache-dependency-path: requirements.txt

            - name: Install the toolchain
              run: pip install -r requirements.txt

            - name: Identify the committer
              run: |
                  git config user.name "github-actions[bot]"
                  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

            # The version a branch publishes: N.M.x publishes N.M, any other name publishes itself.
            - name: The version of this branch
              id: version
              run: |
                  version="${{GITHUB_REF_NAME}}"
                  if [[ "$version" =~ ^[0-9]+\\.[0-9]+\\.x$ ]]; then
                    version="${{version%.x}}"
                  fi
                  echo "The branch '${{GITHUB_REF_NAME}}' publishes the version '$version'."
                  echo "name=$version" >> "$GITHUB_OUTPUT"

            # The highest version branch of the repository, by version order, in which a "1.x" branch comes
            # after "1.2" and "1.2.x": it is where the next minor is written. sort -V alone puts "1.x" first,
            # so each name is sorted by a key where "x" is a large number. A branch without mkdocs.yml is not a
            # published version. Only that branch carries "latest".
            - name: Is this the newest version?
              id: newest
              run: |
                  git fetch --quiet origin '+refs/heads/*:refs/remotes/origin/*'
                  newest=$(git for-each-ref --format='%(refname:lstrip=3)' 'refs/remotes/origin/*' \\
                    | grep -E '^[0-9]+\\.([0-9]+(\\.x)?|x)$' \\
                    | while read -r branch; do git cat-file -e "origin/$branch:mkdocs.yml" 2>/dev/null && echo "$branch"; done \\
                    | awk '{{ key = $0; if (key ~ /^[0-9]+\\.x$/) sub(/x$/, "999999", key); else sub(/\\.x$/, "", key); print key " " $0 }}' \\
                    | sort -V -k1,1 \\
                    | tail -n 1 \\
                    | cut -d' ' -f2)
                  echo "The newest version branch is '$newest', this one is '${{GITHUB_REF_NAME}}'."
                  if [ "$newest" = "${{GITHUB_REF_NAME}}" ]; then
                    echo "latest=true" >> "$GITHUB_OUTPUT"
                  else
                    echo "latest=false" >> "$GITHUB_OUTPUT"
                  fi

            # The token needs nothing but "contents: write" on the site repository. The GITHUB_TOKEN of this
            # repository cannot write another one.
            - name: Publish this version into the site
              env:
                  SITE_TOKEN: ${{{{ secrets.DOCS_PAGES_TOKEN }}}}
                  VERSION: ${{{{ steps.version.outputs.name }}}}
                  LATEST: ${{{{ steps.newest.outputs.latest }}}}
              run: |
                  set -euo pipefail
                  if [ -z "${{SITE_TOKEN}}" ]; then
                    echo "DOCS_PAGES_TOKEN is not set: nothing can be published." >&2
                    exit 1
                  fi
                  git remote add site \\
                    "https://x-access-token:${{SITE_TOKEN}}@github.com/${{SITE_REPOSITORY}}.git"

                  publish() {{
                    if [ "${{LATEST}}" = "true" ]; then
                      mike deploy --push --update-aliases \\
                        --deploy-prefix "${{PREFIX}}" -r site -b gh-pages "${{VERSION}}" latest \\
                        && mike set-default --push \\
                        --deploy-prefix "${{PREFIX}}" -r site -b gh-pages latest
                    else
                      mike deploy --push --update-aliases \\
                        --deploy-prefix "${{PREFIX}}" -r site -b gh-pages "${{VERSION}}"
                    fi
                  }}

                  # mike works on a local gh-pages, so it must start from the one of the site; without this
                  # it would build a branch of its own and the push would be refused. Ten repositories write
                  # that branch, so a push that loses a race starts again from what the winner left. A push
                  # refused for want of a right is not a race and never will be: it stops here.
                  log="${{RUNNER_TEMP}}/publish.log"
                  for attempt in 1 2 3 4 5; do
                    git fetch --quiet site gh-pages
                    git branch --quiet --force gh-pages FETCH_HEAD

                    if publish 2>&1 | tee "$log"; then
                      echo "Published ${{VERSION}}."
                      exit 0
                    fi

                    if grep -qE 'denied|403|not authorized' "$log"; then
                      echo "DOCS_PAGES_TOKEN cannot write ${{SITE_REPOSITORY}}. It needs 'contents: write'" >&2
                      echo "on that repository, and its resource owner must be the organization that owns" >&2
                      echo "it; an organization may also have to approve it." >&2
                      exit 1
                    fi

                    echo "Another repository wrote gh-pages first, attempt ${{attempt}} of 5; starting again."
                    sleep $(( attempt * 5 ))
                  done

                  echo "The site could not be written after five attempts." >&2
                  exit 1
'''

EXCLUDE = """
# custom_dir lives inside docs_dir, so its templates would be copied to the site as files.
exclude_docs: |
  overrides/
"""

OG_OLD = '  <meta property="og:image" content="{{ config.site_url }}assets/brand/og-slabs-1200x630.png">'
OG_NEW = """  {#- mike rewrites site_url per version and leaves no trailing slash on it. -#}
  {% set base = config.site_url if config.site_url.endswith("/") else config.site_url ~ "/" %}
  <meta property="og:image" content="{{ base }}assets/brand/og-slabs-1200x630.png">"""


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    repo, prefix = Path(sys.argv[1]), sys.argv[2]
    if not (repo / ".git").exists():
        print(f"{repo}: not a git repository", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[a-z0-9-]+", prefix):
        print(f"{prefix}: a prefix is lower case, digits and hyphens", file=sys.stderr)
        return 1

    done, left = [], []

    # 1. mkdocs.yml: the site is one directory of the central one, and the templates are not pages.
    path = repo / "mkdocs.yml"
    text = path.read_text(encoding="utf-8")
    before = text
    old_url = re.search(r"^site_url: (\S+)$", text, re.M)
    if not old_url:
        left.append("mkdocs.yml: no site_url to replace")
    else:
        text = re.sub(r"^site_url: \S+$", f"site_url: {SITE}{prefix}/", text, count=1, flags=re.M)
    if "exclude_docs" not in text:
        text = text.replace("docs_dir: docs\nsite_dir: site\n",
                            "docs_dir: docs\nsite_dir: site\n" + EXCLUDE, 1)
    if text != before:
        path.write_text(text, encoding="utf-8")
        done.append(f"mkdocs.yml: site_url -> {SITE}{prefix}/, exclude_docs")
    if old_url and old_url.group(1).rstrip("/") != f"{SITE}{prefix}".rstrip("/"):
        former = old_url.group(1)
    else:
        former = None

    # 2. The share image: mike leaves no trailing slash on site_url, and the two were concatenated.
    path = repo / "docs/overrides/main.html"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if OG_OLD in text:
            path.write_text(text.replace(OG_OLD, OG_NEW, 1), encoding="utf-8")
            done.append("main.html: the share image gets its slash back")
        elif "og:image" not in text:
            left.append("main.html: no og:image at all")
    else:
        left.append("docs/overrides/main.html: missing")

    # 3. The publication.
    path = repo / ".github/workflows/pages.yml"
    wanted = WORKFLOW.format(prefix=prefix)
    if not path.exists() or path.read_text(encoding="utf-8") != wanted:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(wanted, encoding="utf-8")
        done.append(f"pages.yml: deploys into the site under {prefix}/")

    # 4. The domain goes, and site-root with it.
    if (repo / "site-root").exists():
        subprocess.run(["git", "-C", str(repo), "rm", "-rq", "site-root"], check=True)
        done.append("site-root/: removed")

    # 5. The README. Only what is certain; the rest is reported.
    path = repo / "README.md"
    text = path.read_text(encoding="utf-8")
    before = text
    if former:
        text = text.replace(f"on GitHub Pages:\n**<{former}>**",
                            "as one directory of the Slabs\n"
                            f"documentation site: **<{SITE}{prefix}/>**", 1)
        text = text.replace(former, f"{SITE}{prefix}/")
    text = re.sub(r"^\| `site-root/` \|.*\|\n", "", text, flags=re.M)
    text = text.replace(
        "| `.github/workflows/pages.yml` | The publication: one version per branch, through mike |",
        "| `.github/workflows/pages.yml` | The publication: one version per branch, through mike, into "
        f"the `gh-pages` of `Spomky-Labs/docs` under the prefix `{prefix}` |")
    if "DOCS_PAGES_TOKEN" not in text:
        text = text.rstrip("\n") + (
            "\n\n## Publishing\n\n"
            "This repository publishes no site of its own: it deploys into the `gh-pages` of\n"
            f"[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `/{prefix}/`. It needs a "
            "`DOCS_PAGES_TOKEN`\nsecret, a fine-grained token with `contents: write` on that repository "
            "and nothing else; the\n`GITHUB_TOKEN` of this repository cannot write another one.\n\n"
            "How the documentations came to share one site is in\n"
            "[CONSOLIDATING.md](https://github.com/Spomky-Labs/docs/blob/main/CONSOLIDATING.md).\n")
    if text != before:
        path.write_text(text, encoding="utf-8")
        done.append("README.md: the new address, its table, the token")
    for stale in re.findall(r"https?://[a-z0-9.-]*\.spomky-labs\.com[^\s)>\]]*", text):
        if "docs.spomky-labs.com" not in stale:
            left.append(f"README.md still names {stale}")

    print(f"{repo} -> /{prefix}/")
    for line in done:
        print(f"  changed  {line}")
    for line in left:
        print(f"  LOOK AT  {line}")
    if not done:
        print("  nothing to change: this branch is already in the site")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
