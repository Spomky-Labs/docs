---
description: How to report a bug, send a pull request, and write for this documentation.
---

# Contributing

Thank you for contributing.

## Reporting

Bugs and feature requests go to the
[issues of the library](https://github.com/Spomky-Labs/pki-framework/issues).

**A security problem is not an issue.** Do not open a public issue, pull request or discussion for one:
doing so hands a working exploit to every user of the library before a fix exists. Report it privately,
either through
[GitHub private vulnerability reporting](https://github.com/Spomky-Labs/pki-framework/security/advisories/new)
or by email to `security AT spomky-labs.com`. The
[security policy](https://github.com/Spomky-Labs/pki-framework/security/policy) says what a report should
contain and what happens next.

## The code

Pull requests go to the branch of the maintained line.

- Follow [PSR-12](https://www.php-fig.org/psr/psr-12/). `make cs` fixes what it can.
- Run the test suite: `make tests`.
- Write or update tests. A fix without a test that fails before it is not a fix.
- Static analysis must pass: `make st`.
- Mutation testing runs in continuous integration: `make mu`.
- Rebase your branch before you open the pull request, and write commit messages that say what changed
  and why. You may be asked to squash.

```bash
git clone https://github.com/Spomky-Labs/pki-framework.git
cd pki-framework
composer install
make tests
```

[`CONTRIBUTING.md`](https://github.com/Spomky-Labs/pki-framework/blob/HEAD/.github/CONTRIBUTING.md) holds
the same rules, and the
[code of conduct](https://github.com/Spomky-Labs/pki-framework/blob/HEAD/CODE_OF_CONDUCT.md) applies to
every exchange.

## This documentation

Every documentation of Slabs lives in one repository,
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `projects/<project>/<version>/`. These
pages are in `projects/pki/1.6/`. The pencil at the top right of a page opens its source there.

```bash
git clone https://github.com/Spomky-Labs/docs.git
cd docs
make install                 # the toolchain, in .venv
make serve p=pki v=1.6   # http://127.0.0.1:8000, rebuilt as you save
make check                   # the strict build continuous integration runs
```

`make check` is the gate: a broken internal link, an anchor that does not exist, a page absent from the
navigation or a navigation entry without a page fails the build.

One directory of that repository is one version of the library. A correction that applies to every
version is made in each of them: the versions are directories, not branches.

Titles are in sentence case; names keep their capitals. Every code block is expected to run against the
version the page documents.
