# Migrating a documentation from GitBook

How a documentation published by GitBook becomes a documentation site of Slabs: MkDocs and Material for
MkDocs, in the look of the Slabs brand guidelines v2.0, published on GitHub Pages under its own domain.
This file is the record of what was decided, the steps that work, and the traps already met. It is not
part of the published site.

**The reference implementation is [Spomky-Labs/access-control-doc](https://github.com/Spomky-Labs/access-control-doc),
branch `1.0`.** Every file named below is copied from there. For a repository whose branches are named
like `3.2.x`, or whose project has no mark yet, take `pages.yml`, `slabs.css` and `logo.html` from
[Spomky-Labs/web-push-doc](https://github.com/Spomky-Labs/web-push-doc) instead.

**The conversion is done by [`tools/gitbook2material.py`](tools/gitbook2material.py)**, in this repository,
and **a mark of the design kit is copied for the web by [`tools/web-svg.py`](tools/web-svg.py)**.

## Where things are

| Documentation | Repository | Domain | State |
|---|---|---|---|
| Access Control Framework | `Spomky-Labs/access-control-doc` | `acf.spomky-labs.com` | Migrated; last pull request open (Spomky-Labs/access-control-doc#9) |
| Web Push Framework | `Spomky-Labs/web-push-doc` | `web-push.spomky-labs.com` | Migrated; last pull requests open (Spomky-Labs/web-push-doc#5) |
| JWT Framework | `web-token/jwt-doc` | `web-token.spomky-labs.com` | Migrated; last pull requests open (web-token/jwt-doc#59 to #62) |
| WebAuthn Framework | `web-auth/doc` | `webauthn-doc.spomky-labs.com` | Migrated; last pull requests open (web-auth/doc#64 to #66) |
| PWA Bundle | `Spomky-Labs/phpwa-doc` | `pwa.spomky-labs.com` | Migrated; last pull requests open (Spomky-Labs/phpwa-doc#23 to #25) |
| Central site | `Spomky-Labs/docs` | `docs.spomky-labs.com` | Published |

Every documentation is migrated. What is left, for each one: remove the domain from its GitBook space, then
`SUMMARY.md` and `.gitbook.yaml` in a last pull request, from the least to
the most GitBook formatting to convert.

The central site lists every library and holds the legal notice, the privacy policy and the contact page
that every documentation site links to from its footer. A library that gets a documentation site moves to
the first group of cards of `docs/index.md`.

## What was decided

- **The sources are converted to the syntax of Material for MkDocs.** No GitBook syntax stays in a
  repository: `{% hint %}`, `{% code %}`, `{% content-ref %}` and the HTML GitBook writes are rewritten
  once, branch by branch.
- **The look is the Slabs brand guidelines v2.0.** `slabs-tokens.css` is the file of the design kit,
  copied as it is; `slabs.css` applies it and cites the page of the guidelines each rule comes from. No
  project has a colour of its own.
- **The project name of the guidelines names the site**: the title of the home page, `site_name` and the
  link of the footer say Access Control Framework, Web Push Framework, JWT Framework, WebAuthn Framework,
  PWA Bundle.
- **No illustration of a third party**: the images follow p. 25 of the guidelines; the Freepik
  illustration of the home page of Web Push went.
- **The general contact is `bonjour@spomky-labs.com`**, the address of the guidelines.
- **The header carries the project mark** of the library (Slabs monogram, name, "by Slabs"), in its colour
  and reversed versions, from `4-Web/svg/marques-de-projet` of the design kit. Every project of p. 46 of
  the guidelines has one: WebAuthn Framework, COSE, JWT Framework, OTPHP, CBOR PHP, PKI Framework, Access
  Control Framework, PWA Bundle, Web Push Framework. The central site carries the Slabs logotype.
- **Names and packages are those of the table p. 46**: the project name on first mention and in the
  header, the short form after (ACF, PWA, Web Push, JWT, WebAuthn), and the package a reader installs
  (`spomky-labs/web-push-lib`, `web-auth/webauthn-lib`).
- **The footer** is the reversed Slabs signature, the links of the project, a first link "All
  documentation" to `docs.spomky-labs.com`, and the legal line whose three links lead to the central site.
- **Text is set at 18 px**, 16 px on a phone (p. 34 of the guidelines); code at 14 px; the navigation at
  15 px. The navigation, on the left, and the contents of the page, on the right, are 288 px wide each;
  the reading column 864 px on a wide screen.
- **Every title is in sentence case.** Names keep their capitals.
- **The maintained versions are published**, among those that exist in git (JWT Framework: 4.0 to 4.3,
  not 1.x to 3.3). Every other GitBook variant is redirected to the same page of the latest version, or
  to its home page when that page no longer exists there: `site-root/404.html` asks with a HEAD request.
- **Nothing a reader loads reaches a third party**: fonts are served by the site, and the header does not
  ask the API of GitHub for the stars of the repository. The privacy policy says so; keep it true.

## The steps, for one repository

1. **List the published addresses**, from the sitemap of the GitBook site:
   `https://<domain>/sitemap.xml`, then each `sitemap-pages.xml` it names, one per variant. A variant is
   served under its own prefix (`/v4.5/`, `/3.1.x/`, `/v4.0-erin-elderflower/`), the default one at the
   root. The addresses are the source of truth for the redirects, not `SUMMARY.md`: a GitBook path does
   not always follow the directory (ACF published `the-symfony-bundle/` for `symfony-bundle/`).
2. **Map each variant to a branch.** Look at what each branch holds: a branch can be a stub while its
   variant lives only in GitBook (`web-push-doc` `3.1.x`). Publish the branches with content; send the
   other variants to `latest`.
3. **Move the pages to `docs/`** in a commit of pure renames (`git mv`), so `git log --follow` keeps their
   history. Commit it alone: a rename mixed with edits is seen as a deletion and an addition.
4. **Convert the GitBook syntax** (table below): `python3 -I ~/Projects/docs/tools/gitbook2material.py docs`
   rewrites the pages, moves the images it finds to `docs/assets/images/`, and lists what it left for a
   human: any other `{% %}`, and the HTML GitBook writes outside code blocks. Read the diff, then every
   converted page in the browser. The script is idempotent: running it again changes nothing.
5. **Copy the toolchain** from the reference: `mkdocs.yml` (then adapt the names, `site_url`, `repo_url`,
   `edit_uri`, `extra.slabs`, and the navigation, which `gitbook2material.py --nav "<names>" docs` writes
   from `SUMMARY.md`), `requirements.txt`, `Makefile`,
   `.editorconfig`, `.gitignore`, `.github/workflows/` (three files; they replace
   `auto-switch-default-branch.yml`), `docs/assets/`, `docs/overrides/`, `site-root/`.
6. **Fill `site-root/`**: `CNAME` with the domain, and in `404.html` the `VARIANTS` table, GitBook prefix
   to published version.
7. **Add the redirects** for the addresses that no longer match a page, in `redirect_maps` of `mkdocs.yml`.
8. **Put the titles in sentence case**, in the pages; the navigation takes the title of each page from its
   first heading. `gitbook2material.py --titles "Web Push,Symfony,Doctrine" docs` does it and prints every
   change; the list holds the proper nouns of the project. Read the list: a hyphenated name ("Web-Push")
   or a parenthesis ("TTL (Time-to-live)") still needs a hand.
9. **`make check`**, then check every address of the sitemap against a local publication (below).
10. **Several versions**: convert the oldest published branch first. Each next one starts from its own
    branch, merges the converted branch of the previous version (`git merge --no-commit`), then puts back
    under `docs/` the GitBook content of its own version, converts it again, regenerates its navigation and
    points `edit_uri` at itself. Check each branch by converting its GitBook content from scratch in a
    scratch directory and comparing it with `docs/`, file by file: they must be identical. A change common
    to every version is made on the oldest branch and merged forward. One pull request per version, merged
    in order. When the branches do not contain each other (WebAuthn Framework), each one is converted on
    its own, the same way, and a common change is made on each.
11. **Pull request, merge, then the domain** (below). Then remove the domain from the GitBook space, and
    in a last pull request `SUMMARY.md` and `.gitbook.yaml`.
12. **Move the library** to the documentation sites on the central site, if it was not there.

## From GitBook to Material

| GitBook | Material for MkDocs |
|---|---|
| `{% hint style="info" %}` … `{% endhint %}` | `!!! info`, the content indented by four spaces; `warning`, `danger`, `success` and `tip` keep their name |
| `{% code title="f" lineNumbers="true" %}` and its fence | ` ```lang title="f" linenums="1" ` ; `overflow` and `fullWidth` are dropped |
| `<pre class="language-x" data-title="f" data-line-numbers><code>` with lines in `<strong>` | a fence with `title`, `linenums`, and `hl_lines` for the lines whose text is in bold (by the script) |
| `{% content-ref url="x.md" %}` | a plain link |
| `<figure><picture>` with a dark `<source>` | two Markdown images, `#only-light` and `#only-dark`, in a figure of Material (by the script) |
| `<figure><img><figcaption>` on one line | `<figure markdown="span">` holding a Markdown image and its `<figcaption>` (by the script): MkDocs rewrites the path of a Markdown image, never the `src` of an HTML one |
| `<picture>` with a dark `<source>` | two images, `#only-light` and `#only-dark` |
| `<table>`, on one line or several, with `<th width>` | a Markdown table, `<code>`, `<em>`, `<strong>` and links kept (by the script) |
| `<p>a</p><p>b</p>` in a cell | `a<br>b` (by the script) |
| `<mark style="color:red">` (or a variable of GitBook, `color:$info`) | the text in bold; any other colour, the text alone (by the script): colour never carries a meaning |
| a link to a directory (`signed-tokens/`) | a link to its `README.md` (by the script) |
| `(<../.gitbook/assets/name (1).png>)`, a path with spaces | the same image under `assets/images/name-1.png` (by the script) |
| `.gitbook/assets/…` | `docs/assets/images/`, renamed without spaces or `(1)`, unused files dropped |
| `layout: landing` | `hide: [navigation, toc]` |
| `description:` | kept |
| `SUMMARY.md` | `nav:` of `mkdocs.yml` |
| `README.md` | stays the home page |

Twig in a code block (`{% if %}`, `{% block %}`) is code, not GitBook: convert only outside fences.

## Checking a publication locally

mike runs only with the toolchain on the `PATH` (it calls `properdocs`):

```bash
export PATH="$PWD/.venv/bin:$PATH"
git clone --branch <branch> . /tmp/site && cd /tmp/site     # a clean clone, without gh-pages
mike deploy --update-aliases <version> latest && mike set-default latest
git archive gh-pages | tar -x -C /tmp/root && cp -R site-root/. /tmp/root/
```

Serve `/tmp/root` with a server that answers `404.html` with the status 404 for a missing path, the way
GitHub Pages does, then open every address of the sitemap in a browser: the redirects of `404.html` run in
JavaScript, a plain HTTP client does not follow them.

## Publishing a domain

0. **Verify the domain in the organization of the repository**, before anything else. Spomky-Labs has
   verified `spomky-labs.com`, which reserves the domain and its subdomains for its own repositories: a
   repository of web-token or web-auth cannot use `web-token.spomky-labs.com` until that organization has
   verified it too (Settings of the organization, Pages, Add a domain, then the TXT record
   `_github-pages-challenge-<organization>.<domain>` at Infomaniak). Without it, Pages keeps an empty
   custom domain and the site answers 404 as soon as the DNS points to GitHub.
1. Merge: the push to the version branch publishes `gh-pages` and its root. **Merge the pull requests of
   several versions one by one, each after the publication of the previous one**: the workflow keeps one
   run waiting in its concurrency group, and a newer one cancels it (JWT 4.2 was cancelled by 4.3).
   Check `versions.json` on `gh-pages`, and run the workflow again on a missing branch
   (`gh workflow run pages.yml --ref <branch>`).
2. Lower the TTL of the record the day before.
3. **Point the DNS first**: a CNAME to `<organization>.github.io.` (`spomky-labs`, `web-auth`, `web-token`).
4. **Then** declare the domain: Settings, Pages, deploy from `gh-pages`, root folder, custom domain. The
   API does it too: `gh api -X POST repos/<repo>/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'`
   reads the domain from `CNAME`.
5. Wait for the certificate, then enforce HTTPS.
6. Check every address of the sitemap on the live site, then remove the domain from GitBook.

A record changed at Infomaniak can take a quarter of an hour to reach its own servers
(`web-push.spomky-labs.com`). Ask them directly before declaring the domain: the public resolvers keep the
old answer for the TTL of the record, an hour by default.

A domain declared before its DNS existed got no certificate for a long while (`docs.spomky-labs.com`):
removing it and adding it again by the API did not start one. If the certificate does not come, remove
the domain and add it again in the Settings page.

## Traps already met

- **Never name a directory `gh-pages/`** at the root of a repository: mike asks `git rev-parse gh-pages`,
  git answers with the directory, mike believes the branch exists and the first publication fails. The
  root of the site lives in `site-root/`.
- **A PHP block without `<?php` is not coloured** by Pygments; GitBook coloured it.
  `extend_pygments_lang` with `startinline: true` in `mkdocs.yml` fixes it.
- **Line numbers drift** from their lines in the table layout; `linenums_style: pymdownx-inline` writes
  them on the line itself.
- **Material wins on specificity** in a few places: `.md-typeset ul:not([hidden])`, the titles of
  admonitions, the tab labels it turns into anchors. A rule of `slabs.css` that seems ignored usually needs
  a stronger selector.
- **Some files of the web set of the design kit still carry a C2PA manifest**, the marks of Access
  Control Framework, PWA Bundle and Web Push Framework among them. `tools/web-svg.py <source> <target>`
  removes it, with the title and the role, and refuses to write if the drawing would change.
- **A branch left from GitBook can take `latest`.** PWA Bundle kept a `1.x` branch from GitBook, never
  migrated, which sorts after `1.6`: no published version carried `latest` and the root of the site led
  nowhere. `pages.yml` now keeps only the branches that hold a `mkdocs.yml` (Spomky-Labs/phpwa-doc#22); the
  other repositories take the same change with their last pull request. To repair a site at once:
  `mike alias --push <version> latest` and `mike set-default --push latest` on a clone of the repository.
- **`sort -V` puts `1.x` before `1.2`.** The newest version branch, the one that carries `latest`, is
  found by sorting on a key where `x` is a large number (`pages.yml` of `web-push-doc`). The reference and
  Beffroi still have the plain sort; no branch named `N.x` exists yet to show it.
- **A branch named `3.2.x`** publishes the version `3.2` (`pages.yml` of `web-push-doc`).
- **The name beside the logo** is hidden only beside a project mark: the mark images carry the class
  `sl-logo--mark`, and `slabs.css` tests it with `:has()`.
- **`git checkout --theirs` takes the whole file**, not the side of the conflict: on `mkdocs.yml` it brings
  back the navigation and the `edit_uri` of the other version. Take `--ours` and resolve the lines by hand.
- **The README of the GitBook home page and the README of the repository have the same name**: a script
  that puts the GitBook content back under `docs/` must not remove the second one.
- **`git add -A docs` takes what was staged before**, deleted files included. After a conversion, add the
  pages by name for a commit about pages, and check `git show --stat` before pushing.
- **`DEFAULT_BRANCH_TOKEN` does not exist**, neither on the repositories nor on the organizations:
  `default-branch.yml`, like the workflow it replaced, does nothing until it is created.
- **A documentation repository may have no licence of its own** (`web-push-doc`): the README says what is
  licensed and does not claim more.
- **Strict mode finds the links GitBook let rot**: a page that moved, an anchor whose heading changed, a
  `broken-reference` GitBook wrote for a page it lost. Fix them in a commit of their own, **branch by
  branch from the tree of that branch**: a fix written for 1.5 of PWA Bundle pointed links of 1.4 at pages
  1.4 does not have. A link to a page that only exists in a later version keeps its text, without a link.
- **Names of GitBook files hold spaces, apostrophes and parentheses** (`Capture d'écran (1).png`): copy a
  GitBook tree with `git archive <branch> -- <paths> | tar -x`, never with a loop over file names.
- **Do not chain a branch switch after a step that leaves a merge uncommitted**: git refuses it, but a
  silenced error hides that it did.
- **A page of the GitBook root may not exist in the latest version** (the root of WebAuthn served 5.3,
  `latest` is 5.4): list, among the addresses of the root and of the published variants, the ones that
  land on a home page, and redirect each to its new page.
- **Strict mode fails on a page outside the navigation**: `not_in_nav` or `exclude_docs` for the ones that
  must stay out.
- **The revision dates need a commit**: a strict build of uncommitted pages fails on the git plugin.
- **A pull request can be merged before the last push reaches it.** Check what the base branch holds after
  a merge, and open a new pull request for what is missing.

## Still open

- The Slabs icon library, which is in neither the design kit nor Spomky-Labs/brand-kit: the interface
  icons of the theme stay until then.
