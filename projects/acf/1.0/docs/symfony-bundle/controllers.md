# Controllers

## Declaring the policy on the action

```php
use AccessControl\Attribute\AccessPolicy;
use AccessControl\Attribute\Argument;

final class PostController extends AbstractController
{
    #[AccessPolicy('EDIT', new Argument('post'), message: 'Only the author may edit this post.')]
    public function edit(Post $post): Response
    {
        // ...
    }
}
```

The listener reads the attribute, resolves `new Argument('post')` against the controller arguments, asks the question, and throws before your code runs. A denial comes out as a `403`, the exception carrying `#[WithHttpStatus(403)]`.

On the class rather than the method, the policy applies to every action. The attribute is repeatable, and composes with `All`, `AtLeastOneOf` and `When`. See [Access Policies](../pure-php/access-policies.md).

## `#[IsGranted]` keeps working

From the moment the bundle is registered, Symfony's `#[IsGranted]` is read by this component, not by Security. Nothing in your code changes.

```php
#[IsGranted('EDIT', 'post')]
public function edit(Post $post): Response
```

The bridge listener matches Security's own behaviour, including the parts that are easy to get wrong: a subject given as an `Expression` is evaluated rather than taken as an argument name, and `methods` is matched case-insensitively.

Two listeners answering the same attribute would ask the requester twice for one question, and the profiler would show two. So the bundle removes Security's, rather than letting both run.

**What is lost, and it is confined.** Security's listener fills `setAttributes()`, `setSubject()` and `setAccessDecision()` on the exception it throws; this component's exception carries none of that. Nothing in Symfony reads those three accessors, so the loss only reaches application code that reads them in an `AccessDeniedHandlerInterface` or an error template.

## `isGranted()` and `denyAccessUnlessGranted()` without Security

`AbstractController::isGranted()` and `denyAccessUnlessGranted()` raise a `LogicException` telling you to install SecurityBundle when Security is absent, whichever other stack the application registered. That check lives in FrameworkBundle, which this project does not patch.

Add the trait, and nothing else changes:

```php
use AccessControl\Bundle\Controller\AccessControlTrait;

final class PostController extends AbstractController
{
    use AccessControlTrait;

    public function edit(Post $post): Response
    {
        $this->denyAccessUnlessGranted('EDIT', $post);
        // ...
    }
}
```

A trait method wins over the one inherited from the parent class, so the call sites stay as they are. With Security present, the trait defers to it.

## Injecting the checker

For a controller that is not an `AbstractController`, or anywhere else in the application:

```php
use AccessControl\RequesterBoundChecker;

public function __construct(
    private readonly RequesterBoundChecker $accessChecker,
) {
}

public function edit(Post $post): Response
{
    if (! $this->accessChecker->isGranted('EDIT', $post)) {
        throw new AccessDeniedException();
    }
}
```

`decide()` on the same service hands back the full `AccessDecision`, with the reason and the votes, when a boolean is not enough.

## Asking about somebody else

The checker binds the *current* requester. To ask about another one, build the request yourself:

```php
$decision = $this->accessControlManager->decide(new AccessRequest($otherUser, 'EDIT', $post));
```
