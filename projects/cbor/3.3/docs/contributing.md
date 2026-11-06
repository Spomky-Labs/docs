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

The pages of this site live in their own repository,
[Spomky-Labs/cbor-php-doc](https://github.com/Spomky-Labs/cbor-php-doc), one branch per version of the
library. Every page carries an "Edit this page" link at the top: it opens the source of that page, on the
branch of the version you are reading.

A correction that applies to every version is best made on the oldest branch — it is merged forward from
there. `make check` builds the site strictly, and is what the pull request will be checked by.

## Supporting the project

-   [Become a GitHub sponsor](https://github.com/sponsors/Spomky)
-   [Support on Patreon](https://www.patreon.com/FlorentMorselli)
