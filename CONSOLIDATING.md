# One site, one repository

Nine documentations meant nine repositories, nine domains, nine Pages configurations, nine certificates
and nine DNS records. They are one site now, `docs.spomky-labs.com`, built from this repository alone:
the hub at the root, one directory per project and per version.

```text
mkdocs.yml, docs/          the hub
projects/jwt/4.3/          one documentation, one version
shared/                    what all of them have in common
tools/build.py             builds the lot
```

This file is the record of how it was done and what it cost. **The nine repositories it names no longer
exist**, so what reads here as an instruction is an account of what was done, not something left to do;
the traps at the end are kept for what they taught, and say so when the thing they bit is gone.
[MIGRATING.md](MIGRATING.md) covers the move off GitBook that came before; [README.md](README.md) says how
to work on the pages today.

## It happened in two steps

**First the domains.** Each repository kept its branches and deployed into the `gh-pages` of this one with
`mike deploy --deploy-prefix`, which gave every project its own directory, its own `versions.json` and its
own search index. Nine domains became one.

**Then the repositories.** Every version of every project was imported under `projects/<prefix>/<version>/`
and the nine repositories were retired. mike went with them: `tools/build.py` writes the `versions.json`
and the redirection of each project itself, which is all the version selector of the theme reads.

| Project | Prefix | Versions |
|---|---|---|
| Access Control Framework | `/acf/` | 1.0 |
| CBOR PHP | `/cbor/` | 3.3, 3.4 |
| COSE | `/cose/` | 4.9 |
| JWT Framework | `/jwt/` | 4.0, 4.1, 4.2, 4.3 |
| OTPHP | `/otphp/` | 11.6 |
| PKI Framework | `/pki/` | 1.6 |
| PWA Bundle | `/pwa/` | 1.4, 1.5, 1.6 |
| Web Push Framework | `/web-push/` | 3.2 |
| WebAuthn Framework | `/webauthn/` | 5.2, 5.3, 5.4 |

Seventeen versions, 932 pages. The import was checked against the site as it was then: the sitemap of
every version matched address for address, and the rendered text of pages taken at random matched to the
character.

## What the move cost

**The revision date of every page was reset.** The plugin reads `git log` for the file, and in a new
repository each file has one commit: every page says the day of the import until it is next edited.
Merging the old histories would not have helped — those commits name `docs/x.md`, not
`projects/jwt/4.3/docs/x.md` — and only rewriting every path through every history would, at the price of
JWT four times over and more than three thousand commits. It was accepted as a one-time flattening that
corrects itself page by page.

**The issues and the pull requests of the nine repositories went with them.** The seven open issues were
carried over first; GitHub transfers an issue only between repositories of the same owner, so one was
transferred and six were copied with their threads, their author credited and pinged. Pull requests cannot
be transferred at all.

**Two faults of the toolchain were fixed on the way.** `og:image` was a 404 on every site — mike rewrote
`site_url` per version without a trailing slash and `main.html` concatenated it — and the templates of the
theme were published beside the pages, `custom_dir` living inside `docs_dir`. They now sit outside it.

## What becomes of the former domain

Seven were deleted outright — `acf`, `cbor`, `cose`, `otphp`, `pki`, `pwa` and `web-push` answer nothing
at all. A domain that served under GitBook before it served here carries addresses published elsewhere,
and two were kept for that: `web-token.spomky-labs.com` and `webauthn-doc.spomky-labs.com`, which answer
`301` to `/jwt/` and `/webauthn/` with the path kept.

**What matters for a documentation is the path, not the status code.** A reader following a link to one
page who lands on a home page has lost the page *and* the version, and has to search for both. Three ways
were tried, in this order.

### The web redirection of the Manager: no

Infomaniak offers a web redirection on a domain, 301 or 302, set from the Manager. **It discards the
path**: `web-token.spomky-labs.com/4.0/introduction/security-recommendations/` and
`web-token.spomky-labs.com/4.3/` both answered `301` to the single address configured. Its advanced
options offer only *visible* or *invisible (iframe)*, with a title and meta tags for the iframe — nothing
about the path. The documentation says nothing either way, which is why it was found in production.

### A page that redirects, on GitHub Pages: works, but is not a 301

GitHub Pages issues no redirect of its own. The `gh-pages` of the former repository is emptied of its site
and given two pages by [`tools/domain-shell.py`](tools/domain-shell.py): `index.html` sends the root to
the project, and `404.html`, which Pages serves for every other address, prefixes the path it was asked
for. Every address lands on its page, versions included.

It stays the fallback, and the one to use when there is no hosting: it needs nothing but the repository.
A reader without JavaScript sees the page rather than being sent on, and search engines see no 301.

### A rewrite on a web hosting: both

Point the former domains at an Infomaniak hosting and put
[`tools/former-domains.htaccess`](tools/former-domains.htaccess) at its document root. A real 301, and the
path kept, which the Manager's redirection cannot do:

```apache
RewriteCond %{HTTP_HOST} ^web-token\.spomky-labs\.com$ [NC]
RewriteRule ^(.*)$ https://docs.spomky-labs.com/jwt/$1 [R=301,L]
```

Both domains share one document root, so each rule tests the host it answers for and no other site on
that hosting is touched. In a `.htaccess` the pattern sees the path without its leading slash, so `$1` is
the whole of it, and mod_rewrite appends the query string by itself.

This is what answers today for the two domains kept. The rules live on a hosting, not in a repository:
**nothing in git will tell you if they break** — a site rebuilt, a hosting migrated, a `.htaccess`
overwritten. It is the only link of the chain that is not versioned.

## How a repository was retired

Nothing is left to retire. Each of the nine went this way, and no step was taken before the one above it
was checked:

1. The pages were imported under `projects/<prefix>/<version>/` and the site was built strictly.
2. The sitemap of every version was compared, address for address, with the site as it stood.
3. The pull request was merged and the published site was checked in a browser.
4. The open issues were carried over — see what the move cost, above.
5. Only then did the repository go, with its custom domain in its Pages settings and its `gh-pages`.

## Traps

Each of these cost something.

- **A shallow checkout dates every page today.** The revision date is read from `git log`, so the
  workflows fetch the whole history.
- **The git plugin fails a strict build on uncommitted pages**, which makes importing a tree and building
  it in one go impossible: commit first.
- **`actions/checkout` persists the `GITHUB_TOKEN` of its own repository** into
  `http.https://github.com/.extraheader`. That header applies to every github.com URL and takes precedence
  over the credentials carried by the URL of a remote, so the push to the site left as
  `github-actions[bot]` and was refused: "Permission to Spomky-Labs/docs.git denied". The token was set and
  correct; it was simply never used. `persist-credentials: false` keeps the header out, and a public
  repository needs nothing from it afterwards. It cost the first publication of OTPHP. Nothing crosses
  repositories now: `pages.yml` writes the `gh-pages` of its own repository with the token it is given.
- **A queued run is cancelled by a newer one in its group, whatever `cancel-in-progress` says.** That flag
  protects the run that is *in progress*, not the one waiting behind it. `jwt-doc` 4.2 was cancelled by 4.3
  twice, a fortnight apart: once when leaving GitBook, once moving into this site. One build publishes the
  whole site now and its group no longer cancels, so a run lost costs a publication and not a version;
  `gh workflow run pages.yml --ref main` does it again.
- **A push refused for want of a right is not a race.** A retry loop must tell the two apart, or a 403 is
  tried five times over a minute and reported as contention. The loop went with the ten repositories; what
  it taught did not.
- **mike needed a local `gh-pages` seeded from the site.** Without `git fetch site gh-pages` and
  `git branch -f gh-pages FETCH_HEAD`, mike built a branch of its own and the push was refused as a
  non-fast-forward, with a message about "work that you do not have locally". mike went with the nine
  repositories: `tools/build.py` writes every `versions.json` itself.
- **Ten repositories wrote one branch**, and a concurrency group only serialises the runs of one
  repository. One writes it now, so the group does what it says.
- **`og:image` was a 404 on every site**: `site_url` came out of mike without a trailing slash and
  `main.html` concatenated it. Fixed here, for all of them.
- **The templates of the theme were published beside the pages**, `custom_dir` living inside `docs_dir`.
  They sit outside it now, in `overrides/` and `shared/overrides/`.
- **A project directory is matched by its `versions.json`**, not by a list: nothing to maintain here when
  a project arrives or leaves.
- **`git switch -c` then committing in a later step is not safe** when another session works in the same
  clone: the branch is created, `HEAD` moves back, and the commit lands on the branch that was there. Check
  `git branch --show-current` immediately before committing.
- **A branch name that is also a directory name is ambiguous to git.** `gh pr create --fill` fails with
  "use '--' to separate paths from revisions" on a branch called `docs/...` in a repository that has a
  `docs/` directory. Pass `--title` and `--body`.
- **`gh pr create` takes the current branch as its head**, not the one just pushed. Pass `--head`.
