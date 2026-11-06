# Testing

The component ships the test tooling it uses itself, under `AccessControl\Test` and `AccessControl\Bundle\Test`. It is published on purpose: asserting that a door was closed, and which door, is not something an application should have to rebuild.

## Asserting on an answer you hold

`AccessOutcomeAssertionsTrait` matches an `AccessOutcome` or an `AccessDecision` you have in your hand.

```php
use AccessControl\Test\AccessOutcomeAssertionsTrait;

final class PostVoterTest extends TestCase
{
    use AccessOutcomeAssertionsTrait;

    public function testTheAuthorMayEdit(): void
    {
        $outcome = new PostVoter()->vote(new AccessRequest($author, 'EDIT', $post));

        self::assertAccessGranted($outcome);
    }
}
```

| Assertion | |
|---|---|
| `assertAccessGranted($answer)` | |
| `assertAccessDenied($answer)` | |
| `assertAccessAbstained($answer)` | An abstention is a result of its own, so assert it rather than settling for "not granted" |

## Asserting on a request that has run

`AccessControlAssertionsTrait` matches the questions a functional test asked, not an answer you hold. A `403` says the door was closed; these say **which** door, and why.

```php
use AccessControl\Bundle\Test\AccessControlAssertionsTrait;

final class PostControllerTest extends WebTestCase
{
    use AccessControlAssertionsTrait;

    public function testAStrangerCannotEdit(): void
    {
        $client = static::createClient();
        $client->request('GET', '/posts/1/edit');

        self::assertResponseStatusCodeSame(403);
        self::assertAccessWasDeniedOn('EDIT');
    }
}
```

| Assertion | |
|---|---|
| `assertAccessWasDeniedOn($attribute)` | |
| `assertAccessWasGrantedOn($attribute)` | |
| `assertAccessWasNotDeniedOn($attribute)` | |
| `assertAccessWasDeniedBy($voter)` | Which voter closed the door |
| `assertAccessDecisionCount($count)` | Catches a question asked twice, or not at all |
| `getAccessDecisionEvents()` | The whole log, to assert on something the others do not cover |

The two traits are named apart on purpose: `AccessOutcomeAssertionsTrait` is about an answer in your hand, `AccessControlAssertionsTrait` about a request that has run.

When an assertion fails, it lists every decision that was reached, with its reason. "No access decision was reached at all" is its own message, because a controller with no access policy and an entry point whose listener is not registered both look like that.

## Testing a policy handler

`AccessPolicyHandlerTestTrait` gives a handler two tests for free and a way to evaluate a policy without a container.

```php
use AccessControl\Test\AccessPolicyHandlerTestTrait;

final class NotHandlerTest extends TestCase
{
    use AccessPolicyHandlerTestTrait;

    protected function createHandler(): AccessPolicyHandlerInterface
    {
        return new NotHandler();
    }

    public static function provideSupportedPolicies(): iterable
    {
        yield [new Not(new AccessPolicy('EDIT'))];
    }

    public function testItInvertsTheNestedPolicy(): void
    {
        $outcome = $this->evaluate(new Not(new FixedOutcomeAccessPolicy(AccessOutcome::grant())));

        self::assertAccessDenied($outcome);
    }
}
```

The two inherited tests check that the handler claims the policies it says it handles, and that it leaves a foreign one to another handler. `FixedOutcomeAccessPolicy` is a policy that answers what you tell it to, so a composite can be tested without writing voters.

## Testing a combining algorithm

`AccessDecisionStrategyTestTrait` runs a table of voter outcomes through a strategy.

```php
use AccessControl\Test\AccessDecisionStrategyTestTrait;

final class NightShiftStrategyTest extends TestCase
{
    use AccessDecisionStrategyTestTrait;

    public static function provideStrategyTests(): iterable
    {
        yield [new NightShiftStrategy(), [/* the voters */], true];
    }
}
```

## Watching without the framework

Everything above reads the events the manager dispatches. Give the manager a dispatcher, collect `AccessDecisionEvent`, and you have the same log outside any framework. See [The Manager](the-manager.md#watching-what-happens).
