# The documentation of JWT Framework

The public documentation of [JWT Framework](https://github.com/web-token/jwt-framework), JSON Web Tokens for
PHP and Symfony: signature (JWS), encryption (JWE), keys (JWK) and algorithms (JWA), the components, the
Symfony bundle and the console commands.

Published with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) as one directory of the Slabs
documentation site: **<https://docs.spomky-labs.com/jwt/>**

## Writing

```bash
make install   # the toolchain, in .venv, from requirements.txt
make serve     # http://127.0.0.1:8000, rebuilt as you save
make check     # the strict build continuous integration runs
```

`make check` is the gate: a broken internal link, an anchor that does not exist, a page absent from the
navigation or a navigation entry without a page fails the build.

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
| `.github/workflows/pages.yml` | The publication: one version per branch, through mike, into the `gh-pages` of `Spomky-Labs/docs` under the prefix `jwt` |
| `.github/workflows/default-branch.yml` | A new version branch becomes the default branch |

How the documentation left GitBook, and the rules every documentation site of Slabs follows, are in
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs/blob/main/MIGRATING.md).

## One branch per version

A branch of this repository is a version of the packages: `4.0`, `4.1`, `4.2`, `4.3`. A push to one of
them publishes it under its own name, and the newest one also carries the `latest` alias, which the root
of the site redirects to. A fix that applies to several versions is merged forward.

```bash
git switch -c 4.4 4.3         # from the version it continues
# in mkdocs.yml, point edit_uri at the new branch
git push -u origin 4.4        # publishes it, and moves "latest" and the default branch
```

## Publishing

This repository publishes no site of its own: it deploys into the `gh-pages` of
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `/jwt/`. It needs a `DOCS_PAGES_TOKEN`
secret, a fine-grained token with `contents: write` on that repository and nothing else; the
`GITHUB_TOKEN` of this repository cannot write another one.

How the documentations came to share one site is in
[CONSOLIDATING.md](https://github.com/Spomky-Labs/docs/blob/main/CONSOLIDATING.md).
