# The two migrations

There are two, and confusing them would cost you the adoption. One is free and happens on day one. The other is yours to make, at your own pace, or never.

## Day one is free

```bash
composer require spomky-labs/access-control-bundle
```

Register the bundle. That is all.

Your configuration does not move. Your code does not move. The answers do not move. **What changed is who decides.**

* Your voters keep being consulted, wrapped so they answer questions asked here.
* `#[IsGranted]` is read by this component.
* `is_granted()` answers in your templates.
* The rules of your `security.yaml` are enforced.
* Your role hierarchy is read from the service Security already built.

A `security.yaml` stays byte for byte what it was. Nothing is deprecated, nothing warns, nothing has to be rewritten.

If a migration guide starts with "adapt your voters", nobody migrates. So this one does not.

## Then, at your own pace

The second migration is moving to this component's own vocabulary, and it is optional, file by file:

| From | To |
|---|---|
| `Security\...\VoterInterface` | [`AccessControl\VoterInterface`](../access-control-in-a-nutshell/voters.md) |
| `#[IsGranted]` | [`#[AccessPolicy]`](../pure-php/access-policies.md) and its combinators |
| `affirmative`, `unanimous`, `consensus`, `priority` | [The XACML names](../access-control-in-a-nutshell/combining-algorithms.md) |
| `security.access_control` | [`access_control.rules`](../symfony-bundle/url-rules.md) |
| `security.role_hierarchy` | [`access_control.role_hierarchy`](../symfony-bundle/configuration.md#role-hierarchy) |
| A token as the requester | [Anything at all](../access-control-in-a-nutshell/requesters.md) |

There is no deadline. A codebase halfway through works: the two vocabularies answer the same voters.

## The destination

An application that no longer has Symfony Security at all, and still expresses everything it used to.

That is not a thought experiment: it is a tested shape. Every piece is verified under **three** shapes, and it is the third that finds what is missing.

| Shape | What it says |
|---|---|
| SecurityBundle alone | The reference behaviour |
| Both bundles | The migration is seamless: same configuration, one bundle more, same answers |
| This bundle alone | The destination is reachable |

The controller and the template are never written twice for the two stacks. That they do not change **is** the claim being tested.

## What to do first

1. Install the bundle and change nothing else.
2. Open a page with the profiler and check the [Configuration tab](../symfony-bundle/profiler.md#the-configuration-tab) says the component answers.
3. Run your test suite. It should be green, and if it is not, the difference is a bug worth reporting.
4. Then, only if you want to, start [moving your voters](from-security.md).

## What will not move on its own

Two things raise rather than degrading quietly, and you want to know before you install:

* **Field level ACL** in templates, `is_granted('EDIT', $post, 'title')`, is refused out loud. An application using it cannot install the bundle.
* Declaring the same thing on both `security.*` and `access_control.*` raises at compile time: two combining algorithms, two role hierarchies, two sets of URL rules, contradictory `allow_if_all_abstain`.

See [Known Divergences](known-divergences.md) for the full list of what differs, all of it deliberate.
