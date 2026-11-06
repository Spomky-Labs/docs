# Access Control Framework

**Access Control** decides whether a requester is allowed to perform an action on a subject.

It is authorization on its own. Voters, combining algorithms, access policies declared as attributes, and decisions that say why they were reached: none of it needs an authentication stack to exist. There is no user, no token and no firewall in the vocabulary, and a requester is whatever your application says it is.

```php
$decision = $accessControlManager->decide(new AccessRequest($requester, 'EDIT', $post));

if (! $decision->isGranted()) {
    throw new AccessDeniedException($decision->reason);
}
```

The same question, asked from a controller of a Symfony application:

```php
#[AccessPolicy('EDIT', new Argument('post'))]
public function edit(Post $post): Response
{
    // ...
}
```

## Two packages

| Package | What it is |
|---|---|
| `spomky-labs/access-control-lib` | The library, usable in any PHP application |
| `spomky-labs/access-control-bundle` | The integration into the Symfony full-stack framework |

Both are read-only subtree splits of [access-control-framework](https://github.com/spomky-labs/access-control-framework), where issues and pull requests belong.

## Coming from Symfony Security

Installing the bundle changes nothing you can see. Your voters keep being consulted, `#[IsGranted]` is read, `is_granted()` answers in your templates, and the rules of your `security.yaml` are enforced. What changed is who decides. Moving to this component's own vocabulary is a second, separate migration you make at your own pace, and [The Two Migrations](migration/the-two-migrations.md) explains why confusing the two would cost you the adoption.

## Where to start

* [What is Access Control?](the-project/the-project.md) if you want the shape of the thing first.
* [Installation](the-project/installation.md) if you want to try it now.
* [Vocabulary](access-control-in-a-nutshell/vocabulary.md) if a word here already means something else to you. It probably does: `subject` is the resource, not the actor.
