# Moving a documentation into the one site

Nine documentations meant nine domains, nine Pages configurations, nine certificates and nine DNS records.
They are becoming one site, `docs.spomky-labs.com`, which holds the hub at its root and one directory per
project. **The repositories do not move**: each keeps its branches, one per version, its `mkdocs.yml` and
its continuous integration, and deploys into the `gh-pages` of this repository under its own prefix.

```text
/                      the hub, the legal notice, the privacy policy, the contact page
/otphp/11.6/           a version, deployed from Spomky-Labs/otphp-doc branch 11.6.x
/otphp/latest/         the alias /otphp/ redirects to
/otphp/versions.json   what that project publishes
```

`mike deploy --deploy-prefix <project>` writes a `versions.json` per directory, so **every project keeps
its own version axis, its own version selector and its own search index**. Nothing is merged: a 949 KB
search index stays with the project it belongs to.

This file is the record of how OTPHP was moved, written so the eight others follow the same path. How the
documentations left GitBook is in [MIGRATING.md](MIGRATING.md).

## Where things stand

A prefix is the label of the former subdomain, so every redirection is one rule and no path changes.
`web-token` and `webauthn-doc` are the two exceptions: the project is JWT Framework, not its organization,
and `-doc` named a repository, not a documentation.

| Project | Repository | Prefix | Branches to move | State |
|---|---|---|---|---|
| OTPHP | `Spomky-Labs/otphp-doc` | `/otphp/` | `11.6.x` | **Moved.** Redirection pending |
| Access Control Framework | `Spomky-Labs/access-control-doc` | `/acf/` | `1.0` | Pull request open |
| PKI Framework | `Spomky-Labs/pki-framework-doc` | `/pki/` | `1.6.x` | Pull request open |
| Web Push Framework | `Spomky-Labs/web-push-doc` | `/web-push/` | `3.2.x` | Pull request open |
| COSE | `web-auth/cose-doc` | `/cose/` | `4.9.x` | Pull request open |
| CBOR PHP | `Spomky-Labs/cbor-php-doc` | `/cbor/` | `3.3.x`, `3.4.x` | Pull request open |
| PWA Bundle | `Spomky-Labs/phpwa-doc` | `/pwa/` | `1.4`, `1.5`, `1.6` | Pull request open |
| WebAuthn Framework | `web-auth/doc` | `/webauthn/` | `5.2`, `5.3`, `5.4` | Pull request open |
| JWT Framework | `web-token/jwt-doc` | `/jwt/` | `4.0`, `4.1`, `4.2`, `4.3` | Pull request open |

Sixteen branches, one pull request each, all open and green. **A branch is in this table only if
`versions.json` of the live site publishes it.** Several repositories hold version-looking branches that publish nothing — `phpwa-doc` has `1.x`,
`1.1`, `1.2` and `1.3`, `web-push-doc` has `3.1.x` — and they stay as they are.

Take the easy ones first: the four projects with a single branch prove the recipe copies, before the ones
with four.

**The reference implementation is [Spomky-Labs/otphp-doc](https://github.com/Spomky-Labs/otphp-doc),
branch `11.6.x`.** Its `pages.yml`, its `mkdocs.yml` and its `main.html` are what the others copy.

## Done once

Both are done. They are here because nothing below works without them.

### This repository

`Spomky-Labs/docs` owns the root of `gh-pages` and nothing else (#13, #14, #15):

- `pages.yml` replaces the root entries that are **not** a project, a project being a directory that holds
  a `versions.json`. `mkdocs gh-deploy --force` replaced the whole branch and would have erased every
  project at each publication of the hub.
- `site-root/404.html` replaces the one of the theme and is the only 404 of the site.
- Ten repositories write the branch, so a push that loses a race is retried.

### The token

**A fine-grained token with `contents: write` on `Spomky-Labs/docs` and nothing else**, as the secret
`DOCS_PAGES_TOKEN`. Its resource owner must be the organization, and the organization may have to approve
it. The `GITHUB_TOKEN` of a repository cannot write another one.

```bash
gh secret set DOCS_PAGES_TOKEN --org Spomky-Labs --visibility selected \
  --repos access-control-doc,cbor-php-doc,otphp-doc,phpwa-doc,pki-framework-doc,web-push-doc
gh secret set DOCS_PAGES_TOKEN --repo web-auth/doc
gh secret set DOCS_PAGES_TOKEN --repo web-auth/cose-doc
gh secret set DOCS_PAGES_TOKEN --repo web-token/jwt-doc
```

A fine-grained token expires, and the day it does the publications stop, all of them, without warning.

## Moving one project

On each branch of the table, **one pull request per branch, and they are independent**: the edits are the
same on every branch of a repository, so a branch does not have to wait for the one below it and they can
be merged in any order. This is the one place where the rule of MIGRATING.md — oldest first, merged
forward — does not apply: that rule exists for content, which propagates, and these six edits do not.
A later merge between two version branches sees the same new content on both sides and resolves itself.

```bash
git switch -c chore/one-site-many-projects <version branch>
python3 -I ~/Projects/docs/tools/into-the-site.py . <prefix>
```

[`tools/into-the-site.py`](tools/into-the-site.py) makes the six edits below, prints what it changed and
what it left for a human, and changes nothing on a second run. It was written by replaying the move of
OTPHP: on that branch before the move it produces the `mkdocs.yml`, the `main.html` and the `pages.yml`
that were written by hand, to the byte. Read its diff anyway; the README of a repository is prose and it
only does what is certain there.

What it does, and what to check if you do it by hand:

**1. `mkdocs.yml`** — the site is one directory of the central one, and the templates of the theme are not
pages:

```yaml
site_url: https://docs.spomky-labs.com/<prefix>/

# custom_dir lives inside docs_dir, so its templates would be copied to the site as files.
exclude_docs: |
  overrides/
```

**2. `docs/overrides/main.html`** — mike rewrites `site_url` per version and leaves no trailing slash on
it, so the share image was `https://<domain>/11.6assets/...`, a 404 on every site:

```jinja
{% set base = config.site_url if config.site_url.endswith("/") else config.site_url ~ "/" %}
<meta property="og:image" content="{{ base }}assets/brand/og-slabs-1200x630.png">
```

**3. `.github/workflows/pages.yml`** — copy the one of `otphp-doc` and change `PREFIX`. Three things in it
are not obvious and all three cost a failed publication:

- `persist-credentials: false` on the checkout;
- the local `gh-pages` seeded from the site before mike runs;
- a 403 stopping at once instead of being retried as a race.

**4. `git rm -r site-root`** — the domain goes with it. Removing it does not touch the `gh-pages` that
repository already published, which keeps serving the old domain until its DNS moves.

**5. The README** — the new address, the `site-root/` row of its table, and the `DOCS_PAGES_TOKEN` note.

**6. `make check`**, then the pull request, then merge. The publication starts on the merge.

## Checking it

After the first branch of a project reaches the site:

```bash
P=otphp     # the prefix
for p in / /latest/ /versions.json /latest/search/search_index.json; do
  printf '%-40s %s\n' "/$P$p" \
    "$(curl -sS -o /dev/null -w '%{http_code}' "https://docs.spomky-labs.com/$P$p")"
done

# The share image was a 404 on every site before this move: it must be 200 now.
u=$(curl -sS "https://docs.spomky-labs.com/$P/latest/" \
    | grep -o 'property="og:image" content="[^"]*"' | sed 's/.*content="//;s/"//')
echo "$u -> $(curl -sS -o /dev/null -w '%{http_code}' "$u")"

# The templates of the theme must not be served.
curl -sS -o /dev/null -w '%{http_code}\n' "https://docs.spomky-labs.com/$P/latest/overrides/main.html"

# The hub, which the publication must not have touched.
curl -sS -o /dev/null -w '%{http_code}\n' https://docs.spomky-labs.com/
```

Then four addresses **in a browser**: the redirections of the 404 run in JavaScript and a plain HTTP client
does not follow them.

| Address | What must happen |
|---|---|
| `/<prefix>/` | lands on `/<prefix>/latest/` |
| `/<prefix>/<a real page without a version>/` | lands on the same page of `latest` — this is what carries the redirections |
| `/<prefix>/latest/<nothing>/` | stays, and says the page does not exist in this version |
| `/<nothing>/` | stays, and shows the 404 of the hub |

Check the version selector of a project that publishes several versions: it must list that project's
versions and no other.

## The redirection

Only once the above is checked, and once the card of `docs/index.md` leads to `/<prefix>/`.

At the registrar, a **301 preserving the path**:

```text
<old domain>/*   →   docs.spomky-labs.com/<prefix>/*
```

The addresses of the old site already carry their version — `/latest/…`, `/11.6/…` — so they land directly
on a page. An address without a version lands on the 404 of the site, which sends it to `latest`.

Check, in a browser, `<old domain>/latest/` and a deep page such as
`<old domain>/latest/<section>/<page>/`. Then an address of the old sitemap, taken at random.

If the registrar cannot preserve the path, the fallback is a shell on GitHub Pages: the old repository
keeps a `gh-pages` reduced to a page that redirects in JavaScript. It is not a 301 and the old
configurations stay, but nothing else in this file changes.

## Removing the old site

Last, and only after the redirection answers:

1. Remove the custom domain in the Pages settings of the old repository.
2. Delete its `gh-pages`.
3. The repository itself stays: it is where the documentation is written.

## Traps

Each of these cost something.

- **`actions/checkout` persists the `GITHUB_TOKEN` of its own repository** into
  `http.https://github.com/.extraheader`. That header applies to every github.com URL and takes precedence
  over the credentials carried by the URL of a remote, so the push to the site leaves as
  `github-actions[bot]` and is refused: "Permission to Spomky-Labs/docs.git denied". The token is set and
  correct; it is simply never used. `persist-credentials: false` keeps the header out, and a public
  repository needs nothing from it afterwards. It cost the first publication of OTPHP.
- **A push refused for want of a right is not a race.** A retry loop must tell the two apart, or a 403 is
  tried five times over a minute and reported as contention.
- **mike needs a local `gh-pages` seeded from the site.** Without `git fetch site gh-pages` and
  `git branch -f gh-pages FETCH_HEAD`, mike builds a branch of its own and the push is refused as a
  non-fast-forward, with a message about "work that you do not have locally".
- **Ten repositories write one branch.** A concurrency group only serialises the runs of one repository.
- **`og:image` was a 404 on every site**, and still is on the eight that have not moved.
- **The templates of the theme were published beside the pages**, and still are on the eight.
- **A project directory is matched by its `versions.json`**, not by a list: nothing to maintain here when
  a project arrives or leaves.
- **`git switch -c` then committing in a later step is not safe** when another session works in the same
  clone: the branch is created, `HEAD` moves back, and the commit lands on the branch that was there. Check
  `git branch --show-current` immediately before committing.
- **A branch name that is also a directory name is ambiguous to git.** `gh pr create --fill` fails with
  "use '--' to separate paths from revisions" on a branch called `docs/...` in a repository that has a
  `docs/` directory. Pass `--title` and `--body`.
- **`gh pr create` takes the current branch as its head**, not the one just pushed. Pass `--head`.
- **Two default branches are behind their latest version**: `web-token/jwt-doc` is on `4.2` while `4.3` is
  published, `web-auth/doc` is on `5.3` while `5.4` is. `default-branch.yml` needs a
  `DEFAULT_BRANCH_TOKEN` that has never been created. Set them by hand while moving those two.
