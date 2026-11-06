# The documentation of CBOR PHP

The sources of [cbor.spomky-labs.com](https://docs.spomky-labs.com/cbor/), the documentation of
[CBOR PHP](https://github.com/Spomky-Labs/cbor-php): a PHP library that encodes and decodes CBOR, the
binary data format of [RFC 8949](https://datatracker.ietf.org/doc/html/rfc8949).

The site is built with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), in the look of the Slabs brand
guidelines, and published on GitHub Pages.

## Writing

```bash
make install   # the toolchain, in .venv
make serve     # http://127.0.0.1:8000, rebuilt as you save
make check     # a strict build: a broken link or a missing anchor fails
```

`make check` is what the Check workflow runs on a pull request. Run it before you open one.

## One branch per version

Each maintained version of the library has its own branch here, and each branch publishes its own version
of the site: `3.3.x` is served at `/3.3/`, and the newest version also answers as `latest`, which the root
of the domain leads to. A change that belongs to every version is written on the oldest branch and merged
forward.

## Contributing

Issues and pull requests are welcome. A page is edited where it is read: every page of the site carries an
"Edit this page" link that opens its source on the right branch.

The documentation is published under the licence of the library it documents,
[MIT](https://github.com/Spomky-Labs/cbor-php/blob/HEAD/LICENSE). The Slabs marks, typefaces and brand
assets under `docs/assets/brand` and `docs/assets/fonts` are not covered by it: they belong to Spomky-Labs
and to their respective authors.

## Publishing

This repository publishes no site of its own: it deploys into the `gh-pages` of
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `/cbor/`. It needs a `DOCS_PAGES_TOKEN`
secret, a fine-grained token with `contents: write` on that repository and nothing else; the
`GITHUB_TOKEN` of this repository cannot write another one.

How the documentations came to share one site is in
[CONSOLIDATING.md](https://github.com/Spomky-Labs/docs/blob/main/CONSOLIDATING.md).
