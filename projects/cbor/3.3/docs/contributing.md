---
description: How to report, fix and document something in CBOR PHP
---

# Contributing

First of all, **thank you** for contributing.

Bugs and feature requests go to the
[issues of the library](https://github.com/Spomky-Labs/cbor-php/issues). A security report does not: it
follows [the private disclosure process](https://github.com/Spomky-Labs/cbor-php/security/policy)
instead.

## The code

A few rules make a review quick:

-   You MUST follow the [PSR-12](https://www.php-fig.org/psr/psr-12/) coding standards.
-   You MUST run the test suite.
-   You MUST write, or update, unit tests when a bug is fixed or a feature is added.
-   You SHOULD write documentation.

Open a pull request against the branch of the version concerned — a fix on the oldest branch that has the
bug, a feature on the newest — write commit messages that make sense, and rebase before submitting. You
may be asked to squash.

The checks that gate a pull request all run locally through
[Castor](https://castor.jolicode.com/), in the same image the CI uses:

```bash
composer install
castor ecs        # coding standards (castor ecs_fix to apply)
castor rector     # automated refactoring, dry run (castor rector_fix to apply)
castor phpstan    # static analysis
castor deptrac    # architecture layers
castor lint       # syntax check
castor phpunit    # tests, with coverage
```

The full version is in
[CONTRIBUTING.md](https://github.com/Spomky-Labs/cbor-php/blob/HEAD/.github/CONTRIBUTING.md), and what is
expected of everyone taking part is in
[the code of conduct](https://github.com/Spomky-Labs/cbor-php/blob/HEAD/CODE_OF_CONDUCT.md).

## This documentation

Every documentation of Slabs lives in one repository,
[Spomky-Labs/docs](https://github.com/Spomky-Labs/docs), under `projects/<project>/<version>/`. These
pages are in `projects/cbor/3.3/`. Every page carries an "Edit this page" link at the top: it opens the
source of that page.

A correction that applies to every version is made in each of them: the versions are directories, not
branches. `make check` builds the whole site strictly, and is what the pull request will be checked by.

## Supporting the project

-   [Become a GitHub sponsor](https://github.com/sponsors/Spomky)
-   [Support on Patreon](https://www.patreon.com/FlorentMorselli)
