# Templates

## `is_granted()`

Nothing changes. From the moment the bundle is registered, this component answers it.

```twig
{% if is_granted('EDIT', post) %}
    <a href="{{ path('post_edit', {id: post.id}) }}">Edit</a>
{% endif %}
```

```twig
{% if is_granted_for_user(otherUser, 'EDIT', post) %}
```

Leaving both extensions to publish `is_granted()` would raise nothing: Twig silently keeps whichever was initialised last, so the answer would depend on the order of `config/bundles.php`. The bundle therefore replaces Security's Twig extension with one that publishes everything else and not these two.

## Saying *why*, not only *whether*

```twig
{% set decision = access_control_decision('EDIT', post) %}

{% if not decision.isGranted %}
    <p class="notice">{{ decision.reason }}</p>
{% endif %}
```

`access_control_decision_for_user(user, 'EDIT', post)` asks the same question about somebody else.

**They carry names of their own, and not Security's `access_decision()`.** The two shapes diverge: `decision` here is a `DecisionVote` enum where Security's is an `isGranted` boolean, and `reason` is a property where Security's is `getMessage()`. A function whose return type depended on which bundles are installed would be a trap, so both live side by side during a migration and you move at your own pace.

`access_decision()` keeps being published by Security when it is installed, and keeps answering Security's object.

## What is left to Security

When SecurityBundle is installed, these keep working untouched, being authentication rather than authorization:

`impersonation_url()`, `impersonation_path()`, `impersonation_exit_url()`, `impersonation_exit_path()`, `access_decision()`, `access_decision_for_user()`.

Each is delegated by name rather than borrowed wholesale. Twig reads the owner of a function off the object its callable is bound to, and compiles a call that fails at runtime when that object is not a registered extension. The cost of naming them is that a function Security adds in a later release would be left out, so the list is checked against Security's own extension and **a stranger raises at build time** rather than disappearing quietly.

## Field level access control is refused, loudly

Security's `is_granted()` accepts a third `$field` argument, which goes through `symfony/acl`. No voter here understands a `FieldVote`.

Rather than answering `false`, which a template cannot tell from a real refusal, the function raises:

```
Passing a $field to the "is_granted()" function is field level access control,
which goes through symfony/acl and is not carried over by the AccessControl component.
```

**An application using field level ACL in its templates cannot install this bundle.** That is deliberate: a refusal indistinguishable from a real one is the same family of fault as a guard that lets somebody through.

## Without Twig

The functions come from `twig/twig`, which is optional. Without it, nothing is published and nothing fails; the [checker](controllers.md#injecting-the-checker) answers the same questions from PHP.
