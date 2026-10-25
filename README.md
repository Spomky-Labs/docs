# The documentation of Slabs

The central site of the documentation of Slabs: a page that lists every library and its documentation,
and the legal notice, the privacy policy and the contact page that every documentation site links to
from its footer.

Published with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) on GitHub Pages:
**<https://docs.spomky-labs.com/>**

## Writing

```bash
make install   # the toolchain, in .venv, from requirements.txt
make serve     # http://127.0.0.1:8000, rebuilt as you save
make check     # the strict build continuous integration runs
```

## Where things are

| Path | What it is |
|---|---|
| `docs/index.md` | The list of the libraries and of their documentation |
| `docs/legal-notice.md`, `docs/privacy.md`, `docs/contact.md` | The pages every documentation site links to from its footer |
| `docs/assets/stylesheets/` | The look: `slabs-tokens.css`, copied as it is from the Slabs design kit, and `slabs.css`, which applies the guidelines to the theme |
| `docs/assets/brand/`, `docs/assets/fonts/` | The logotype, the signature, the favicons and the share image of the design kit, and its typefaces (SIL Open Font License) |
| `docs/CNAME` | The domain of the site |
| `MIGRATING.md` | How a documentation leaves GitBook: the decisions, the steps, the traps already met. Not published |
| `.github/workflows/check.yml` | The strict build, on every pull request |
| `.github/workflows/pages.yml` | The publication of main to gh-pages |

## Licence

MIT, as the libraries it documents.
