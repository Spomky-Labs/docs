# Installation

## In a Symfony application

```bash
composer require spomky-labs/access-control-bundle
```

Register the bundle. **There is no `enabled` flag: registering it is the opt-in.**

```php
// config/bundles.php
return [
    // ...
    AccessControl\Bundle\AccessControlBundle::class => ['all' => true],
];
```

That is the whole of day one. If your application has SecurityBundle, nothing you can see changes: your voters keep being consulted, `#[IsGranted]` is read, `is_granted()` answers in your templates, and the rules of your `security.yaml` are enforced. What changed is who decides. See [The Two Migrations](../migration/the-two-migrations.md).

## In any PHP application

```bash
composer require spomky-labs/access-control-lib
```

No container and no framework are needed:

```php
use AccessControl\AccessControlManager;
use AccessControl\AccessRequest;
use AccessControl\Strategy\PermitOverridesStrategy;

$accessControlManager = new AccessControlManager(
    strategies: [new PermitOverridesStrategy()],
    voters: [new PostVoter()],
);

$decision = $accessControlManager->decide(new AccessRequest($requester, 'EDIT', $post));
```

See [The Manager](../pure-php/the-manager.md).

## Requirements

* PHP 8.4 or later.
* Symfony 8.1 or later, for the bundle.

## Optional packages

The library requires almost nothing. These unlock features, and their absence is never an error:

| Package | What it unlocks |
|---|---|
| `symfony/security-core` | Reusing voters, tokens and the role hierarchy of Symfony Security |
| `symfony/expression-language` | Attributes and conditions given as an `Expression`, and the `allow_if` option of a URL rule |
| `twig/twig` | The template functions |
| `symfony/workflow` | Guarding workflow transitions |
| `symfony/console` | Guarding console commands |
| `symfony/web-profiler-bundle` | The profiler panel |

**One exception worth knowing about.** Guarding a workflow transition requires `symfony/security-core` to be *installed*, even though this component never uses it there: Symfony's `FrameworkExtension` refuses a guard expression at compile time without it, before this bundle gets a chance to replace the listener. Install it and nothing more. See [Workflow Guards](../symfony-bundle/workflow.md).

## Checking it is on

```bash
bin/console debug:container --tag=access_control.voter
```

Or open a page with the profiler enabled: the panel says which stack answered, and lists every question the request asked. See [The Profiler Panel](../symfony-bundle/profiler.md).
