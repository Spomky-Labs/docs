# Contributing

Requests for new features, bug fixes and all other ideas that make the library more useful are welcome.
Issues go to [the bug tracker](https://github.com/Spomky-Labs/otphp/issues); a security issue goes to
`security@spomky-labs.com` instead, and never to the tracker.

The conventions a pull request is expected to follow are in
[CONTRIBUTING.md](https://github.com/Spomky-Labs/otphp/blob/HEAD/.github/CONTRIBUTING.md).

## Which branch

Branches are named `<major>.<minor>.x`. Open a pull request against the lowest maintained branch your
change applies to: a bug fix against the oldest branch that has the bug, a new feature against the branch
under development. Changes are then merged forward into the newer branches.

## The checks

Quality tasks run through [Castor](https://castor.jolicode.com/), from `castor.php` at the root of the
library. Each one runs in a dockerized image, or natively when Docker is not available.

```bash
castor phpunit      # the test suite, with coverage
castor phpstan      # static analysis, at the maximum level
castor ecs          # coding standards
castor rector       # modernisation, as a dry run
castor deptrac      # the dependency rules between layers
castor prepare-pr   # the fixers, then the analysers: what to run before pushing
```

A single test, by name:

```bash
castor phpunit -- --filter TOTPTest::testGenerateOTPAt
```

Continuous integration runs the suite on PHP 8.2, 8.3 and 8.4, on 8.5 experimentally, and once more on 8.2
with the lowest allowed dependencies.

## This documentation

The pages of this site live in
[Spomky-Labs/otphp-doc](https://github.com/Spomky-Labs/otphp-doc), one branch per version of the library.
Every page has an *edit* pencil at the top that opens it on the right branch.

```bash
make install   # the toolchain, in .venv
make serve     # http://127.0.0.1:8000
make check     # the strict build continuous integration runs
```
