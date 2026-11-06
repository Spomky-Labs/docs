# Access policies

An access policy is a question declared where it applies, as an attribute, rather than asked in the body of a method.

```php
use AccessControl\Attribute\AccessPolicy;
use AccessControl\Attribute\Argument;

#[AccessPolicy('EDIT', new Argument('post'))]
public function edit(Post $post): Response
{
    // ...
}
```

The entry point reads the attribute, asks the question, and refuses before your code runs. In a Symfony application that is done for you on controllers and on console commands.

## `#[AccessPolicy]`

```php
new AccessPolicy(
    attribute: 'EDIT',                  // what is being asked
    subject: new Argument('post'),      // what it is being asked about
    strategy: 'deny_overrides',         // the combining algorithm, optional
    environment: ['ip' => '10.0.0.1'],  // extra circumstances, optional
    allowIfAllAbstain: null,            // null defers to the manager
    message: 'Only the author may edit this post.',
);
```

It is repeatable, and it goes on a class, a method or a function. On a class it applies to every method.

The `attribute` is anything a voter understands: a string, a `Closure`, an `Expression`.

## `Argument`: values known only at runtime

An attribute is static; the subject usually is not. `Argument` names a value the entry point will resolve when the call happens.

```php
#[AccessPolicy('EDIT', new Argument('post'))]
public function edit(Post $post): Response
```

The name is the argument's name. Naming one that does not exist raises an `UnknownArgumentException` rather than passing `null` to the voters, which would silently ask a different question.

## `message`: what the visitor reads

The `reason` a voter gives is a diagnostic and is deliberately withheld from the response. The `message` of a policy is not: it is the text carried by the denial.

```php
#[AccessPolicy('EDIT', new Argument('post'), message: 'Only the author may edit this post.')]
```

## Combining policies

Three combinators compose policies into a tree. All three are repeatable attributes and take a `message` of their own.

### `All`

Every nested policy must grant. It short-circuits on the first denial.

```php
use AccessControl\Attribute\All;

#[All([
    new AccessPolicy('EDIT', new Argument('post')),
    new AccessPolicy('ROLE_EDITOR'),
])]
```

### `AtLeastOneOf`

One granting policy is enough. It short-circuits on the first grant.

```php
use AccessControl\Attribute\AtLeastOneOf;

#[AtLeastOneOf([
    new AccessPolicy('EDIT', new Argument('post')),
    new AccessPolicy('ROLE_ADMIN'),
])]
```

### `When`

Requires the nested policies only when a condition holds, and steps aside otherwise, abstaining rather than denying.

```php
use AccessControl\Attribute\When;
use Symfony\Component\ExpressionLanguage\Expression;

#[When(new Expression('request.isMethod("POST")'), [
    new AccessPolicy('EDIT', new Argument('post')),
])]
```

**The condition speaks about the circumstances of the call, not about the requester.** The entry point hands over its own context: an HTTP method is reached as `request.isMethod("POST")`, a console option as `input.getOption("force")`. This is what `#[IsGranted]`'s `methods` parameter did, generalised, and what tells a web call apart from a console one.

The condition is an `Expression` and not a string, deliberately: a bare string would be silently compiled as one, which is exactly the trap the expression voter had to be fixed for.

### There is no `Not`

Two reasons, and neither is an oversight.

The negation of a three-valued logic is not defined: `Not` would turn "nobody had anything to say" into "access granted". And negative permissions are a known trap: `Not(ROLE_ADMIN)` allows everybody except administrators, anonymous visitors included.

A userland `Not` is a handler and an attribute of your own, needing no change to the component. `Sequentially` is not provided either, being already what `All` and `AtLeastOneOf` do by short-circuiting.

## Writing your own policy and handler

An access policy is any object implementing `AccessPolicyInterface`; a handler is what knows how to evaluate it.

```php
interface AccessPolicyHandlerInterface
{
    public function supports(AccessPolicyInterface $accessPolicy): bool;

    public function handle(
        AccessPolicyInterface $accessPolicy,
        AccessPolicyContext $context,
        AccessPolicyEvaluator $evaluator,
    ): AccessOutcome;
}
```

The evaluator is handed over so a composite handler can evaluate its children through the same path, which is what keeps the profiler tree and the events correct whatever the shape.

In a Symfony application, implementing the interface is enough: autoconfiguration tags the service `access_control.policy_handler`. A policy no handler supports raises an `UnsupportedAccessPolicyException` rather than being ignored.

`AccessPolicyInterface` declares only `message`. A status code or an exit code is a property of the entry point, not of the policy that refused, and each entry point settles its own.
