---
description: 'How to report a bug, send a pull request, and write for this documentation.'
---

# Contributing

Thank you for contributing.

## Reporting

Bugs and feature requests go to the [issues of the library](https://github.com/web-auth/cose-lib/issues).

**A security problem is not an issue.** Do not open a public issue, pull request or discussion for one:
doing so hands a working exploit to every user of the library before a fix exists. Report it privately,
either through
[GitHub private vulnerability reporting](https://github.com/web-auth/cose-lib/security/advisories/new) or
by email to `security AT spomky-labs.com`. The
[security policy](https://github.com/web-auth/cose-lib/security/policy) says what a report should contain
and what happens next.

## The code

Pull requests go to the branch of the maintained line, which
[`RELEASES.md`](https://github.com/web-auth/cose-lib/blob/HEAD/RELEASES.md#minor-release-support-matrix)
names.

- Write or update tests. A fix without a test that fails before it is not a fix.
- The test suite, the coding standards, the static analysis and the mutation testing all run in the
  project QA container, through [Castor](https://castor.jolicode.com/): `castor qa` runs the lot, and
  `castor phpunit` the tests alone.
- Rebase your branch before you open the pull request, and write commit messages that say what changed
  and why. You may be asked to squash.

```bash
git clone https://github.com/web-auth/cose-lib.git
cd cose-lib
composer install
castor phpunit
```

The [code of conduct](https://github.com/web-auth/cose-lib/blob/HEAD/CODE_OF_CONDUCT.md) applies to every
exchange.

## This documentation

Every documentation of Slabs lives in one repository,
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `projects/<project>/<version>/`. These
pages are in `projects/cose/4.9/`. The pencil at the top right of a page opens its source there.

```bash
git clone https://github.com/Spomky-Labs/docs.git
cd docs
make install                 # the toolchain, in .venv
make serve p=cose v=4.9   # http://127.0.0.1:8000, rebuilt as you save
make check                   # the strict build continuous integration runs
```

`make check` is the gate: a broken internal link, an anchor that does not exist, a page absent from the
navigation or a navigation entry without a page fails the build.

One directory of that repository is one version of the library. A correction that applies to every
version is made in each of them: the versions are directories, not branches.

Titles are in sentence case; names keep their capitals. Every code block is expected to run against the
version the page documents.
