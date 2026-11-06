# The manager

`AccessControlManager` is the whole library in one object: it asks the voters, hands their outcomes to a combining algorithm, and returns a decision.

```php
use AccessControl\AccessControlManager;
use AccessControl\AccessRequest;
use AccessControl\Strategy\DenyOverridesStrategy;
use AccessControl\Strategy\PermitOverridesStrategy;

$accessControlManager = new AccessControlManager(
    strategies: [new PermitOverridesStrategy(), new DenyOverridesStrategy()],
    voters: [new PostVoter(), new RoleVoter()],
    defaultStrategy: 'permit_overrides',
);

$decision = $accessControlManager->decide(new AccessRequest($user, 'EDIT', $post));

if (! $decision->isGranted()) {
    throw new AccessDeniedException($decision->reason);
}
```

No container, no framework, no authentication stack. In a Symfony application the bundle builds this for you and you inject `AccessControlManagerInterface`.

## The constructor

| Argument | |
|---|---|
| `strategies` | The combining algorithms to make available, by name. Left empty, `permit_overrides` is registered on its own so the manager is never without one. |
| `voters` | The voters to consult, in order. Order only carries meaning under `first_applicable`. |
| `defaultStrategy` | The algorithm applied when a request names none. Naming one that is not registered raises an `InvalidStrategyException`. |
| `dispatcher` | Optional. Given one, the manager announces every question, vote and decision; this is what feeds the profiler panel and the test assertions. |
| `allowIfAllAbstain` | What to answer when no voter had anything to say. Defaults to `false`. |

Two strategies sharing a name raise an `InvalidStrategyException` rather than letting one quietly win.

`allowIfAllAbstain` belongs to the manager, not to each strategy as it does in Security, so that one setting is obeyed by every entry point rather than by the ones that remembered to pass it. A single request may still override it.

## Asking a question

```php
public function decide(AccessRequest $accessRequest, ?string $strategy = null): AccessDecision;
```

The second argument overrides the default algorithm for this question alone. See [Combining Algorithms](../access-control-in-a-nutshell/combining-algorithms.md).

## Reading the answer

```php
$decision->isGranted();   // bool, an abstention answering false as a denial does
$decision->decision;      // the DecisionVote, if you need to tell the two apart
$decision->reason;        // the strategy's summary, then the concurring reasons
$decision->votes;         // list<CastVote>: the voter, and what it answered
```

`CastVote` pairs a voter with its outcome. The pairing lives on the decision rather than on the outcome because the manager is the only place that knows both: a voter builds an outcome on its own and has no business naming itself, and a handler builds one with no voter at all. It is what lets a decision be read after the fact and still say who refused, which the reason alone cannot when two voters refuse for the same reason.

## Watching what happens

Given an event dispatcher, the manager announces:

| Event | When |
|---|---|
| `AccessQueryEvent` | A question is asked |
| `VoteEvent` | A voter answered |
| `AccessDecisionEvent` | A decision was reached |
| `AccessPolicyEvent` | Each node of an access policy tree was evaluated |

`AccessDecisionEvent` carries its parent when a question was asked from inside another, and `AccessPolicyEvent` does the same for the shape of a policy, which is how the profiler panel shows a tree rather than a flat list.

This is also how the test assertions work without a container: collect the events and assert on them. See [Testing](testing.md).
