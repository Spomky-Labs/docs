# The documentation of PKI Framework

The public documentation of [PKI Framework](https://github.com/Spomky-Labs/pki-framework), X.509
certificates, ASN.1 and public key infrastructure for PHP: certificates, attribute certificates,
certification requests and certification path validation.

Published with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) as one directory of the Slabs
documentation site: **<https://docs.spomky-labs.com/pki/>**

## Writing

```bash
make install   # the toolchain, in .venv, from requirements.txt
make serve     # http://127.0.0.1:8000, rebuilt as you save
make check     # the strict build continuous integration runs
```

`make check` is the gate: a broken internal link, an anchor that does not exist, a page absent from the
navigation or a navigation entry without a page fails the build. The revision dates come from the git
log, so commit a new page before checking it.

Every PHP block of these pages is expected to run against the version the branch documents. The complete
scripts of `docs/examples/` were run as they are written.

## Where things are

| Path | What it is |
|---|---|
| `mkdocs.yml` | The site: theme, extensions, plugins, and the whole navigation |
| `docs/` | The pages, one directory per section of the navigation |
| `docs/assets/stylesheets/` | The look: `slabs-tokens.css`, copied as it is from the Slabs design kit, and `slabs.css`, which applies the guidelines to the theme |
| `docs/assets/brand/`, `docs/assets/fonts/` | The project mark, the signature, the favicons and the share image of the design kit, and its typefaces (SIL Open Font License) |
| `docs/overrides/` | Theme partials: the logo, the footer, the link to the repository |
| `requirements.txt` | The toolchain, pinned. Continuous integration installs exactly this |
| `.github/workflows/check.yml` | The strict build, on every pull request |
| `.github/workflows/pages.yml` | The publication: one version per branch, through mike, into the `gh-pages` of `Spomky-Labs/docs` under the prefix `pki` |
| `.github/workflows/default-branch.yml` | A new version branch becomes the default branch |

The rules every documentation site of Slabs follows are in
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs/blob/main/MIGRATING.md).

## One branch per version

A branch of this repository is a release line of the library, named like its maintenance branch: `1.6.x`
publishes `1.6`. A push to one of them publishes it under its version, and the newest one also carries
the `latest` alias, which the root of the site redirects to.

```bash
git switch -c 1.7.x 1.6.x      # from the version it continues
# in mkdocs.yml, point edit_uri at the new branch
git push -u origin 1.7.x       # publishes it, and moves "latest" and the default branch
```

Only the latest stable line of the library receives fixes, so only the lines
[`SECURITY.md`](https://github.com/Spomky-Labs/pki-framework/blob/HEAD/SECURITY.md) lists are worth a
branch here.

## Licence

The library this documentation describes is released under the MIT licence, reproduced on the
[licence page](docs/migration/license.md). This repository has no licence file of its own.

## Publishing

This repository publishes no site of its own: it deploys into the `gh-pages` of
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `/pki/`. It needs a `DOCS_PAGES_TOKEN`
secret, a fine-grained token with `contents: write` on that repository and nothing else; the
`GITHUB_TOKEN` of this repository cannot write another one.

How the documentations came to share one site is in
[CONSOLIDATING.md](https://github.com/Spomky-Labs/docs/blob/main/CONSOLIDATING.md).
