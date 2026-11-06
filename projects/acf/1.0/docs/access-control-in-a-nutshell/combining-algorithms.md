# Combining algorithms

Several voters answer one question. The combining algorithm turns their outcomes into one decision.

The names are those of XACML, not those of Symfony Security. The correspondence is exact and is given below, so a `security.yaml` moves across without changing meaning.

## The four algorithms

| Name | Security calls it | What it does |
|---|---|---|
| `permit_overrides` | `affirmative` | One grant carries the decision, whatever the others said |
| `deny_overrides` | `unanimous` | One denial binds the decision, whatever the others said |
| `majority` | `consensus` | The heavier side wins, abstentions left out |
| `first_applicable` | `priority` | The first voter that does not abstain settles it |

`permit_overrides` is the default, as `affirmative` is in Security.

### permit\_overrides

Grants as soon as one voter grants. Denies if at least one denied and none granted. If every voter abstained, the answer comes from `allow_if_all_abstain`.

### deny\_overrides

Denies as soon as one voter denies. Grants if at least one granted and none denied. If every voter abstained, the answer comes from `allow_if_all_abstain`.

Despite Security's name for it, this is not unanimity of all voters: abstentions do not block. It is unanimity of the voters that expressed themselves, which is what the mandatory access control models call for, a rule that can be overridden not being mandatory.

### majority

Sums the weights of the grants against the weights of the denials; the heavier side wins. Abstentions are left out. When both sides weigh the same **and at least one voter expressed itself**, the answer comes from `allow_if_equal_granted_denied`, which defaults to granting. When every voter abstained, `allow_if_all_abstain` decides instead.

This is the only algorithm that reads the [weight](voters.md#weights) of an outcome. Security's `consensus` counts votes where this one weighs them; with every weight left at its default of `1`, the two agree. XACML defines no such algorithm.

### first\_applicable

The first grant or denial met is the decision. **Voter order carries the meaning here**, where the three others are order independent: registering a voter before the others is what lets it overrule them. If every voter abstained, `allow_if_all_abstain` decides.

## Choosing where it applies

Once, for the whole application:

```yaml
access_control:
    default_strategy: deny_overrides
```

Or for one question, which overrides the default:

```php
$accessControlManager->decide($accessRequest, 'deny_overrides');
```

Or for one access policy:

```php
#[AccessPolicy('EDIT', new Argument('post'), strategy: 'deny_overrides')]
```

## Three ways to say "A and B", and how to choose

They all work, and picking at random will cost you later. They differ in what they can express and in what they tell you when they refuse.

**`deny_overrides` on the voters.** Use it when the conjunction is a property of your whole authorization model: every rule must agree, always. It is a setting, not something the calling code states, so a reader of the controller cannot see it.

```yaml
access_control:
    default_strategy: deny_overrides
```

**The `All` attribute on the policies.** Use it when *this* entry point requires two distinct questions to be answered yes, and the rest of the application does not. It is visible where the requirement lives, it composes with `AtLeastOneOf` and `When`, and the profiler panel shows the tree rather than a flat list.

```php
#[All([
    new AccessPolicy('EDIT', new Argument('post')),
    new AccessPolicy('ROLE_EDITOR'),
])]
```

**An `Expression`.** Use it when the conjunction is a condition rather than two questions: something about the subject, the request, or arithmetic that no attribute names.

```php
#[AccessPolicy(new Expression('is_granted("EDIT", subject) and subject.isPublished()'))]
```

The rule of thumb: if you can name both halves as attributes, use `All`; if one half is not a question but a condition, use `Expression`; and change `default_strategy` only when you mean it for the entire application.

## When nobody answers

`allow_if_all_abstain` settles what a question answers when no voter had anything to say. It defaults to `false`, and an application that has Security declares it under `security.access_decision_manager` instead, where the bundle reads it.

It can be overridden for one question, which is the only place a `null` means "defer to the manager":

```php
new AccessRequest($requester, 'EDIT', $post, allowIfAllAbstain: true);
```

```php
#[AccessPolicy('EDIT', new Argument('post'), allowIfAllAbstain: true)]
```

## Writing your own

Implement `StrategyInterface`, whose `getName()` is the name a request asks for and `evaluate()` turns the votes into an `AccessDecision`. In a Symfony application that is all: autoconfiguration tags the service `access_control.strategy`.

```php
final readonly class NightShiftStrategy implements StrategyInterface
{
    public function getName(): string
    {
        return 'night_shift';
    }

    public function evaluate(AccessRequest $accessRequest, iterable $votes): AccessDecision
    {
        // ...
    }
}
```

Two strategies registered under the same name raise an `InvalidStrategyException` when the manager is built, rather than letting one quietly win; so does naming a `default_strategy` that nothing registers.
