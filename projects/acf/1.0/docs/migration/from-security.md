# Coming from Security

The mapping, piece by piece. Nothing here is required on day one: see [The Two Migrations](the-two-migrations.md).

## Your voters keep working, unchanged

A voter written against `Symfony\Component\Security\Core\Authorization\Voter\VoterInterface` is wrapped by `VoterAdapter` and consulted exactly as before. The bundle wires every one of them for you.

This is the piece the whole migration rests on. Every application has voters extending Security's `Voter`, and without the adapter they would simply stop being consulted the day the decision manager is pointed here: no error, no deprecation, just access rules that quietly no longer apply.

`CacheableVoterInterface` is honoured: `supportsAttribute()` and `supportsType()` are asked the same strings by both stacks.

## Rewriting one

```php
// Before
final class PostVoter extends Voter
{
    protected function supports(string $attribute, mixed $subject): bool
    {
        return in_array($attribute, ['EDIT', 'DELETE'], true) && $subject instanceof Post;
    }

    protected function voteOnAttribute(string $attribute, mixed $subject, TokenInterface $token): bool
    {
        return $subject->author === $token->getUser();
    }
}
```

```php
// After
final readonly class PostVoter implements VoterInterface
{
    public function supportsAttribute(mixed $attribute): bool
    {
        return in_array($attribute, ['EDIT', 'DELETE'], true);
    }

    public function supportsSubject(mixed $subject): bool
    {
        return $subject instanceof Post;
    }

    public function vote(AccessRequest $accessRequest): AccessOutcome
    {
        $requester = $accessRequest->requester;

        if (! $requester instanceof User) {
            return AccessOutcome::abstain('This voter only knows about users.');
        }

        return $accessRequest->subject->author === $requester
            ? AccessOutcome::grant('The requester is the author.')
            : AccessOutcome::deny('Only the author may edit this post.');
    }
}
```

Three differences worth naming:

* **`supports()` splits in two**, so the two answers can be cached independently.
* **A boolean becomes a three-valued outcome.** Returning `false` from `voteOnAttribute()` meant "deny"; here you choose between `deny()` and `abstain()`, and the difference is real. See [Vocabulary](../access-control-in-a-nutshell/vocabulary.md#the-three-answers-and-why-there-are-three).
* **The requester is not a token.** Type-check what you need and abstain otherwise.

Give a reason. It is what the profiler, the log and the test assertions read.

## Combining algorithms

| `security.yaml` | `access_control` |
|---|---|
| `affirmative` | `permit_overrides` |
| `unanimous` | `deny_overrides` |
| `consensus` | `majority` |
| `priority` | `first_applicable` |

The names are XACML's. The behaviours are identical, with one refinement: `majority` weighs votes where `consensus` counts them, and with every weight left at its default of `1` the two agree.

`allow_if_all_abstain` moves from each strategy to the manager, so one setting is obeyed by every entry point rather than by the ones that remembered to pass it.

**One behaviour differs and it is not ours.** Security's `consensus` grants when both sides are equal; so does `majority`, `allow_if_equal_granted_denied` defaulting to `true`. That default exists because the parity test found the divergence: an earlier version denied on equality.

## Attributes on controllers

`#[IsGranted]` keeps working and is read here. When you want to move:

```php
#[IsGranted('EDIT', 'post')]
#[IsGranted('ROLE_EDITOR')]
```

```php
#[All([
    new AccessPolicy('EDIT', new Argument('post')),
    new AccessPolicy('ROLE_EDITOR'),
])]
```

Two `#[IsGranted]` attributes are an implicit conjunction; `All` says so. `#[IsGranted]`'s `methods` parameter becomes [`When`](../pure-php/access-policies.md#when), which generalises to the console.

## Configuration

```yaml
# Before
security:
    access_decision_manager:
        strategy: unanimous
        allow_if_all_abstain: false
    role_hierarchy:
        ROLE_ADMIN: [ROLE_USER]
    access_control:
        - { path: ^/admin, roles: [ROLE_ADMIN] }
```

```yaml
# After
access_control:
    default_strategy: deny_overrides
    allow_if_all_abstain: false
    role_hierarchy:
        ROLE_ADMIN: [ROLE_USER]
    rules:
        - { path: ^/admin, roles: [ROLE_ADMIN] }
```

**Move, do not copy.** Declaring the same thing on both keys raises at compile time, which is the good case. The one that does not raise is moving a URL rule while leaving the original in place: both then apply and you get the intersection of the permissions, silently. See [URL Rules](../symfony-bundle/url-rules.md#when-both-cover-the-same-path).

And the scopes differ: Security's rules only apply inside a firewall, these apply everywhere.

## Roles

`RoleVoter` reads roles from a Symfony token when it gets one. To stop depending on tokens, implement this component's own contract on your requester:

```php
final readonly class User implements UserWithRoleInterface
{
    /**
     * @return list<string>
     */
    public function getRoles(): array
    {
        return $this->roles;
    }
}
```

A role name and an authentication state stay two vocabularies read by two voters: `ROLE_PREVIOUS_ADMIN` is a role, `IS_IMPERSONATOR` is a state.

## Impersonation

`SwitchUserToken` is understood without any change: `Actor::of()` hands back its original token, and `IS_IMPERSONATOR` is answered from it. To express delegation without Security, implement [`DelegatedRequesterInterface`](../access-control-in-a-nutshell/requesters.md#who-is-really-asking-the-actor).

## Exceptions

`AccessControl\Exception\AccessDeniedException` carries `#[WithHttpStatus(403)]`, so a denial is a `403` even with no firewall to turn it into one. With a firewall present, an anonymous visitor is still sent to the login entry point: the bridge says the refusal a second time in the firewall's own words.

It does not carry `setAttributes()`, `setSubject()` or `setAccessDecision()`. Nothing in Symfony reads them; only application code that does is affected.
