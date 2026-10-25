# Migrating a documentation from GitBook

How a documentation published by GitBook becomes a documentation site of Slabs: MkDocs and Material for
MkDocs, in the look of the Slabs brand guidelines v2.0, published on GitHub Pages under its own domain.
This file is the record of what was decided, the steps that work, and the traps already met. It is not
part of the published site.

**The reference implementation is [Spomky-Labs/access-control-doc](https://github.com/Spomky-Labs/access-control-doc),
branch `1.0`.** Every file named below is copied from there. For a repository whose branches are named
like `3.2.x`, or whose project has no mark yet, take `pages.yml`, `slabs.css` and `logo.html` from
[Spomky-Labs/web-push-doc](https://github.com/Spomky-Labs/web-push-doc) instead.

**The conversion is done by [`tools/gitbook2material.py`](tools/gitbook2material.py)**, in this repository.

## Where things are

| Documentation | Repository | Domain | State |
|---|---|---|---|
| Access Control Framework | `Spomky-Labs/access-control-doc` | `acf.spomky-labs.com` | Migrated |
| Web Push | `Spomky-Labs/web-push-doc` | `web-push.spomky-labs.com` | Pull request open, domain on GitBook |
| JWT Framework | `web-token/jwt-doc` | `web-token.spomky-labs.com` | On GitBook |
| WebAuthn Framework | `web-auth/doc` | `webauthn-doc.spomky-labs.com` | On GitBook |
| PHPWA | `Spomky-Labs/phpwa-doc` | `pwa.spomky-labs.com` | On GitBook |
| Central site | `Spomky-Labs/docs` | `docs.spomky-labs.com` | Published |

Order of the rest: Web Push, then JWT Framework, then WebAuthn Framework, then PHPWA, from the least to
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
- **The header carries the project mark** of the library (Slabs monogram, name, "by Slabs"), in its colour
  and reversed versions. A project without a mark keeps the Slabs logotype and its name beside it until
  one exists. The central site carries the Slabs logotype.
- **The footer** is the reversed Slabs signature, the links of the project, a first link "All
  documentation" to `docs.spomky-labs.com`, and the legal line whose three links lead to the central site.
- **Text is set at 18 px**, 16 px on a phone (p. 34 of the guidelines); code at 14 px; the navigation at
  15 px, in a 288 px column.
- **Every title is in sentence case.** Names keep their capitals.
- **Only the versions that exist in git are published.** A GitBook variant whose content never reached a
  branch is redirected to the same page of the latest version.
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
   converted page in the browser.
5. **Copy the toolchain** from the reference: `mkdocs.yml` (then adapt the names, `site_url`, `repo_url`,
   `edit_uri`, `extra.slabs`, the navigation from `SUMMARY.md`), `requirements.txt`, `Makefile`,
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
10. **Pull request, merge, then the domain** (below). Then remove the domain from the GitBook space, and
    in a last pull request `SUMMARY.md` and `.gitbook.yaml`.
11. **Move the library** to the documentation sites on the central site, if it was not there.

## From GitBook to Material

| GitBook | Material for MkDocs |
|---|---|
| `{% hint style="info" %}` … `{% endhint %}` | `!!! info`, the content indented by four spaces; `warning`, `danger`, `success` and `tip` keep their name |
| `{% code title="f" lineNumbers="true" %}` and its fence | ` ```lang title="f" linenums="1" ` ; `overflow` and `fullWidth` are dropped |
| `<pre class="language-x" data-title="f" data-line-numbers><code>` with lines in `<strong>` | a fence with `title`, `linenums`, and `hl_lines` for the lines in bold |
| `{% content-ref url="x.md" %}` | a plain link |
| `<figure><img><figcaption>` | `![alt](path)` and a caption in the text, or the figure kept as HTML |
| `<picture>` with a dark `<source>` | two images, `#only-light` and `#only-dark` |
| `<table>` with `<th width>` | a Markdown table when the cells allow it, the HTML table otherwise |
| `<mark style="color:…">` | the word itself; colour never carries a meaning |
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

1. Merge: the push to the version branch publishes `gh-pages` and its root.
2. Lower the TTL of the record the day before.
3. **Point the DNS first**: a CNAME to `<organization>.github.io.` (`spomky-labs`, `web-auth`, `web-token`).
4. **Then** declare the domain: Settings, Pages, deploy from `gh-pages`, root folder, custom domain. The
   API does it too: `gh api -X POST repos/<repo>/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'`
   reads the domain from `CNAME`.
5. Wait for the certificate, then enforce HTTPS.
6. Check every address of the sitemap on the live site, then remove the domain from GitBook.

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
- **`sort -V` puts `1.x` before `1.2`.** The newest version branch, the one that carries `latest`, is
  found by sorting on a key where `x` is a large number (`pages.yml` of `web-push-doc`). The reference and
  Beffroi still have the plain sort; no branch named `N.x` exists yet to show it.
- **A branch named `3.2.x`** publishes the version `3.2` (`pages.yml` of `web-push-doc`).
- **The name beside the logo** is hidden only beside a project mark: the mark images carry the class
  `sl-logo--mark`, and `slabs.css` tests it with `:has()`.
- **`git add -A docs` takes what was staged before**, deleted files included. After a conversion, add the
  pages by name for a commit about pages, and check `git show --stat` before pushing.
- **`DEFAULT_BRANCH_TOKEN` does not exist**, neither on the repositories nor on the organizations:
  `default-branch.yml`, like the workflow it replaced, does nothing until it is created.
- **A documentation repository may have no licence of its own** (`web-push-doc`): the README says what is
  licensed and does not claim more.
- **Strict mode fails on a page outside the navigation**: `not_in_nav` or `exclude_docs` for the ones that
  must stay out.
- **The revision dates need a commit**: a strict build of uncommitted pages fails on the git plugin.
- **A pull request can be merged before the last push reaches it.** Check what the base branch holds after
  a merge, and open a new pull request for what is missing.

## Still open

- The general contact address: `contact@spomky-labs.com` (the website) or `bonjour@spomky-labs.com` (the
  guidelines). The contact page uses the first.
- The project marks of Web Push and PHPWA, which the design kit does not have.
- The Slabs icon library, which is not in the design kit: the interface icons of the theme stay until then.
