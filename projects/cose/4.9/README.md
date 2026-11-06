# The documentation of COSE

The public documentation of [COSE](https://github.com/web-auth/cose-lib), CBOR Object Signing and
Encryption for PHP: signing, message authentication codes, encryption and key management, the keys and the
algorithms, after RFC 9052 and RFC 9053.

Published with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) as one directory of the Slabs
documentation site: **<https://docs.spomky-labs.com/cose/>**

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
| `.github/workflows/pages.yml` | The publication: one version per branch, through mike, into the `gh-pages` of `Spomky-Labs/docs` under the prefix `cose` |
| `.github/workflows/default-branch.yml` | A new version branch becomes the default branch |

The rules every documentation site of Slabs follows are in
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs/blob/main/MIGRATING.md).

## One branch per version

A branch of this repository is a version of the library, named like its maintenance branch: `4.9.x`
publishes the version `4.9`. A push to one of them publishes it under its own name, and the newest one also
carries the `latest` alias, which the root of the site redirects to. A fix that applies to several versions
is merged forward.

```bash
git switch -c 4.10.x 4.9.x     # from the version it continues
# in mkdocs.yml, point edit_uri at the new branch
git push -u origin 4.10.x      # publishes it, and moves "latest" and the default branch
```

The maintained branches of the library are listed in
[`RELEASES.md`](https://github.com/web-auth/cose-lib/blob/HEAD/RELEASES.md#minor-release-support-matrix).

## The pages and the library

The pages were written from `doc/` of the library repository, which is where they come from. The code they
show is expected to run against the version the branch documents; the library's own test suite runs the
verifier of [What the application must check](docs/signing/what-the-application-must-check.md) and checks
the algorithm, key type and curve tables against the classes and the IANA registry.

## Licence

The library is published under the MIT licence. These pages document it; the typefaces under
`docs/assets/fonts/` carry the SIL Open Font License, whose text sits beside them.

## Publishing

This repository publishes no site of its own: it deploys into the `gh-pages` of
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `/cose/`. It needs a `DOCS_PAGES_TOKEN`
secret, a fine-grained token with `contents: write` on that repository and nothing else; the
`GITHUB_TOKEN` of this repository cannot write another one.

How the documentations came to share one site is in
[CONSOLIDATING.md](https://github.com/Spomky-Labs/docs/blob/main/CONSOLIDATING.md).
