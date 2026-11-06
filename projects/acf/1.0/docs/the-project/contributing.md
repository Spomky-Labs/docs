# Contributing

Everything happens in the main repository, [spomky-labs/access-control-framework](https://github.com/spomky-labs/access-control-framework). The two packages are read-only subtree splits of it, and a pull request opened on one of them is closed automatically.

## Running the tests

The quality tools live in a Docker image that [Castor](https://castor.jolicode.com/) fetches for you. Nothing else is needed.

```bash
castor qa:install       # dependencies
castor qa:phpunit       # the test suite
castor qa:all           # every check the CI runs
castor qa:prepare-pr    # fix what can be fixed, then analyse
```

Individual checks:

```bash
castor qa:ecs           # coding standards
castor qa:rector        # automated refactoring, dry run
castor qa:phpstan       # static analysis, at max level
castor qa:deptrac       # layer boundaries
castor qa:lint          # syntax
```

## What a change is expected to carry

**Tests, always.** Including where the area you touched had none.

**A test that goes through the real path.** A guard that does not run is the failure this project is built against, and it is silent. It has happened once already: the console guard did not run under `--profile`, because the console hands over a wrapped command carrying no attribute, and every unit test passed because they used a bare command the console never provides. Assert on the result, not on the fact that something was called.

**The three shapes, for anything touching the Symfony bridge.** SecurityBundle alone, both bundles, this bundle alone. The first two say the migration is seamless; the third says the destination is reachable, and it is the one that finds what is missing.

## Comments

Comments belong on the class, the property or the method, never inside a method body. If an explanation is needed in the middle of a function, move it up rather than leave it there.

## Vocabulary

The combining algorithms carry their XACML names, not Symfony's. That divergence is deliberate and documented; please do not "fix" it by mimicry. See [Combining Algorithms](../access-control-in-a-nutshell/combining-algorithms.md).

## Security issues

Do not open a public issue for a security problem. The reporting procedure is in [SECURITY.md](https://github.com/spomky-labs/access-control-framework/blob/1.0.x/SECURITY.md).
