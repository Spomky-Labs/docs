# The profiler panel

With `symfony/web-profiler-bundle` installed, an **Access Control** panel appears in the toolbar and shows every question the request asked.

It exists because a denial is deliberately silent in the response. The `403` says the door was closed; the panel says which door, who closed it, and why.

## The toolbar

The number of decisions reached during the request, and how many were granted and denied.

Zero decisions is worth noticing: a controller with no access policy and an entry point whose listener is not registered look exactly alike from the outside.

**The panel judges emptiness on the questions, not on the decisions.** A `When` that steps aside takes no decision at all, yet a question was asked and answered, and an earlier version showed "no access decision was made" on a page that had in fact been guarded.

## The Decisions tab

Every question, in the order they were asked, and for each of them:

* the **attribute** and the **subject**,
* the **verdict** and the **reason**,
* the **combining algorithm** that produced it,
* every **vote**, with the voter that cast it and what it answered,
* **where the question came from**: the entry point and the calling code.

### Nesting is shown, not flattened

A question asked from inside another is shown under it, which is what happens whenever an expression calls `is_granted()`.

The shape of an access policy is shown the same way. `All` and `AtLeastOneOf` are nodes with their branches under them, so:

* `All(A, B)` shows the operator and both branches, not two decisions side by side,
* `AtLeastOneOf(A, B)` where A grants shows the operator with the single branch it reached, rather than looking like a plain `#[AccessPolicy(A)]`,
* `When(false, …)` shows `ABSTAIN When` and the reason it stepped aside, rather than nothing at all.

Your own composite policies get this without writing a line: the evaluator announces every node of the tree.

## The Configuration tab

The default combining algorithm, whether the application named it or is on the default, and the voters that are registered, each linked to its file.

It also says **which stack answered what**, which is the question to ask first during a migration:

| Row | What it tells you |
|---|---|
| decisions | Whether the component, Security, or an application manager of your own decides |
| `is_granted` | Which listener reads `#[IsGranted]` |
| twig | Which extension publishes the template functions |

An application that installed the bundle and sees Security still named there has a bridge that did not take over, which is exactly what you want to find out before shipping.

## In tests

The panel reads the events the manager dispatches, and so do the test assertions: the same log, without the profiler.

```php
self::assertAccessWasDeniedOn('EDIT');
self::assertAccessWasDeniedBy(PostVoter::class);
```

See [Testing](../pure-php/testing.md).
