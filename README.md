# The documentation of Slabs

Every documentation of [Slabs](https://spomky-labs.com/) lives here: the hub at the root of the site, and
one directory per project and per version.

**<https://docs.spomky-labs.com/>**

| | |
|---|---|
| [`/acf/`](https://docs.spomky-labs.com/acf/) | Access Control Framework |
| [`/cbor/`](https://docs.spomky-labs.com/cbor/) | CBOR PHP |
| [`/cose/`](https://docs.spomky-labs.com/cose/) | COSE |
| [`/jwt/`](https://docs.spomky-labs.com/jwt/) | JWT Framework |
| [`/otphp/`](https://docs.spomky-labs.com/otphp/) | OTPHP |
| [`/pki/`](https://docs.spomky-labs.com/pki/) | PKI Framework |
| [`/pwa/`](https://docs.spomky-labs.com/pwa/) | PWA Bundle |
| [`/web-push/`](https://docs.spomky-labs.com/web-push/) | Web Push Framework |
| [`/webauthn/`](https://docs.spomky-labs.com/webauthn/) | WebAuthn Framework |

## Writing

```bash
make install                 # the toolchain, in .venv, from requirements.txt
make projects                # what can be served
make serve p=jwt v=4.3       # that version, on http://127.0.0.1:8000
make serve                   # the hub
make check                   # the strict build continuous integration runs
```

`make check` is the gate, and it builds **everything**: a broken internal link, an anchor that does not
exist, a page absent from the navigation or a navigation entry without a page fails the build, in any
version of any project.

## Where things are

| Path | What it is |
|---|---|
| `mkdocs.yml`, `docs/` | The hub: the home page, the legal notice, the privacy policy, the contact page |
| `projects/<project>/<version>/` | One documentation, one version: its `mkdocs.yml`, its pages, its project mark, its logo partial |
| `shared/` | What every one of them has in common: the fonts, the stylesheets, the shared brand files and four templates. Copied in before each build; the copies are in `.gitignore` |
| `overrides/` | The templates of the hub |
| `tools/build.py` | The build: the hub, then every version, then the `versions.json` and the redirection of each project |
| `site-root/` | The `404.html` of the whole site, copied over the build. The `CNAME` is a page of the hub, in `docs/` |
| `requirements.txt` | The toolchain, pinned. Continuous integration installs exactly this |
| `.github/workflows/check.yml` | The strict build, on every pull request |
| `.github/workflows/pages.yml` | The publication, on a push to `main` |

## Adding a version

Copy the current one and point it at itself:

```bash
cp -R projects/jwt/4.3 projects/jwt/4.4
# in projects/jwt/4.4/mkdocs.yml, set site_url and edit_uri to 4.4
```

The newest version of a project, by version order, takes the `latest` alias and is what `/jwt/` redirects
to. `tools/build.py` works it out; there is nothing else to declare. The version menu in the header lists
every version from the `versions.json` the build writes, and every version that is not the latest one shows
a note above the header that links to it.

A new project is the same, one directory down: `projects/<prefix>/<version>/`, with its mark in
`docs/assets/brand/` and its `overrides/partials/logo.html`. Add its card to `docs/index.md`.

## How this came about

Nine repositories and nine domains became one site, then one repository.
[CONSOLIDATING.md](CONSOLIDATING.md) is the record: what was decided, what it cost, and the traps.
[MIGRATING.md](MIGRATING.md) covers the move off GitBook that came before.

## Licence

The pages describe packages released under the MIT licence. This repository has no licence file of its
own beyond the one it ships.
