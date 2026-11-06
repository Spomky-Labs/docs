# The documentation of OTPHP

The public documentation of [OTPHP](https://github.com/Spomky-Labs/otphp), one-time passwords for PHP:
time-based codes (TOTP, RFC 6238) and counter-based codes (HOTP, RFC 4226).

Published with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) as one directory of the Slabs
documentation site: **<https://docs.spomky-labs.com/otphp/>**

The site lives in [Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), which holds the hub at its root
and one directory per project. This repository owns `/otphp/` and deploys into it; it publishes no site of
its own. The former domain, `otphp.spomky-labs.com`, redirects there.

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
| `.github/workflows/pages.yml` | The publication: one version per branch, through mike, into the `gh-pages` of `Spomky-Labs/docs` under the prefix `otphp` |
| `.github/workflows/default-branch.yml` | A new version branch becomes the default branch |

The rules every documentation of Slabs follows, and how they came to share one site, are in
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs/blob/main/MIGRATING.md).

Publishing needs a `DOCS_PAGES_TOKEN` secret: a fine-grained token with `contents: write` on
`Spomky-Labs/docs` and nothing else. The `GITHUB_TOKEN` of this repository cannot write another one.

## One branch per version

A branch of this repository is a version of the library, named like its maintenance branches: `11.6.x`
publishes `/otphp/11.6/`. A push to one of them publishes it under its version, and the newest one also
carries the `latest` alias, which `/otphp/` redirects to. Each project of the site keeps its own
`versions.json`, so the version selector of this documentation lists these versions and no other.

```bash
git switch -c 11.7.x 11.6.x     # from the version it continues
# in mkdocs.yml, point edit_uri at the new branch
git push -u origin 11.7.x       # publishes it, and moves "latest" and the default branch
```

## Licence

The library this documentation describes is released under the MIT licence, reproduced on the
[licence page](docs/the-project/license.md). This repository has no licence file of its own.
