# Workflow guards

A workflow transition guarded by an expression is answered by this component, so `is_granted()` in a guard reaches the same voters as everywhere else.

```yaml
framework:
    workflows:
        article:
            type: state_machine
            supports: [App\Entity\Article]
            places: [draft, published, discarded]
            transitions:
                publish:
                    guard: "is_granted('PUBLISH', subject)"
                    from: draft
                    to: published
                discard:
                    guard: "false"
                    from: draft
                    to: discarded
```

`subject` in a guard is the object the workflow is applied to. `is_valid(subject)` keeps working: Workflow adds it to the language it borrows from Security, and it has nothing to do with access.

Guards all reach one listener, so each is matched against the transition it was written for.

## The takeover is conditional

Unlike the rest of the bridge, the guard listener is replaced **only when Security is absent**.

| Your application | Which listener runs |
|---|---|
| SecurityBundle alone | Symfony's |
| Both bundles | Symfony's |
| This bundle alone | This component's |

With Security installed, its guard listener already reaches this component through the decision manager, so replacing it would buy nothing and would cost the trust resolver an expression may name.

## `symfony/security-core` has to be installed

This is the one place where a package must be present and is never used.

```bash
composer require symfony/security-core
```

Symfony's `FrameworkExtension` refuses a workflow guard at compile time unless `symfony/security-core` is installed, and it does so **before** this bundle's compiler pass gets a chance to replace the listener. Without it the container simply does not build:

```
The "security.token_storage" service is needed to be able to use the workflow guard listener.
```

Install it and nothing more: `WorkflowGuardPass` then swaps the listener, and the package sits there unused.

The proper fix is upstream, and it is not a matter of naming this package in `FrameworkExtension`: what is needed there is a generic extension point, not a mention of a package that lives outside Symfony.

That check widening must not open a hole, so the opposite case is pinned by a test: **a guard with neither Security nor this bundle to apply it still refuses to compile**, rather than compiling into a transition nobody guards.
