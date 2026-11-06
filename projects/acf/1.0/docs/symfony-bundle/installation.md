# Installation

```bash
composer require spomky-labs/access-control-bundle
```

```php
// config/bundles.php
return [
    // ...
    AccessControl\Bundle\AccessControlBundle::class => ['all' => true],
];
```

**There is no `enabled` flag. Registering the bundle is the opt-in**, and it is what makes the component take over the authorization entry points.

## What registering it changes

Immediately, and without touching a line of your code or your configuration:

| Entry point | Before | After |
|---|---|---|
| `#[IsGranted]` | Security's listener | [This component's](controllers.md#isgranted-keeps-working) |
| `is_granted()` in Twig | Security's extension | [This component's](templates.md) |
| `security.access_control` rules | Security's access map | This component's decision manager |
| `security.role_hierarchy` | Security | [Shared: one tree, both stacks](configuration.md#role-hierarchy) |
| Your voters | Consulted by Security | [Consulted here, unchanged](../migration/from-security.md) |
| Workflow guards | Security's listener | Security's, unless you have no Security |

The answers do not change. Your `security.yaml` stays byte for byte what it was. See [The Two Migrations](../migration/the-two-migrations.md).

## Check it took over

Open any page with the profiler on: the **Configuration** tab of the Access Control panel names which stack answers what. If it still says `security` where you expected `component`, the bridge did not take over and you want to know now rather than later. See [The Profiler Panel](profiler.md).

## One case where it will not install

An application using **field level ACL** in its templates, that is `is_granted('EDIT', $post, 'title')`, cannot register this bundle: no voter here understands a `FieldVote`, and rather than answering `false`, which a template cannot tell from a real refusal, the function raises. See [Templates](templates.md#field-level-access-control-is-refused-loudly).

## If you have no Security at all

Everything above still applies, minus the takeovers. Two things need a word:

* `AbstractController::isGranted()` and `denyAccessUnlessGranted()` need [a trait](controllers.md#isgranted-and-denyaccessunlessgranted-without-security),
* workflow guards need `symfony/security-core` **installed** though never used, see [Workflow Guards](workflow.md).

Then tell the component who is asking, since there is no token to read: see [Requesters and Actors](../access-control-in-a-nutshell/requesters.md#telling-the-component-who-is-asking).

## Configuration

None is required. Everything has a default, and the settings live under one root key. See [Configuration](configuration.md).
