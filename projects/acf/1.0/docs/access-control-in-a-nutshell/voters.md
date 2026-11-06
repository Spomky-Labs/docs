# Voters

A voter answers one question: given this request, do you grant, deny, or have nothing to say?

```php
interface VoterInterface
{
    public function vote(AccessRequest $accessRequest): AccessOutcome;

    public function supportsAttribute(mixed $attribute): bool;

    public function supportsSubject(mixed $subject): bool;
}
```

## Writing one

```php
use AccessControl\AccessOutcome;
use AccessControl\AccessRequest;
use AccessControl\VoterInterface;

final readonly class PostVoter implements VoterInterface
{
    public function vote(AccessRequest $accessRequest): AccessOutcome
    {
        $post = $accessRequest->subject;
        $requester = $accessRequest->requester;

        if (! $requester instanceof User) {
            return AccessOutcome::abstain('This voter only knows about users.');
        }

        return $post->author === $requester
            ? AccessOutcome::grant('The requester is the author.')
            : AccessOutcome::deny('Only the author may edit this post.');
    }

    public function supportsAttribute(mixed $attribute): bool
    {
        return in_array($attribute, ['EDIT', 'DELETE'], true);
    }

    public function supportsSubject(mixed $subject): bool
    {
        return $subject instanceof Post;
    }
}
```

In a Symfony application, that is all: implementing the interface is enough, autoconfiguration tags the service `access_control.voter`.

## The two `supports` methods are a filter, not an answer

They exist so the manager can skip a voter without instantiating the question, and their answers are cached per attribute and per subject type. They are not where the decision goes.

Returning `true` from both and abstaining in `vote()` is correct and sometimes the only option: `supportsSubject()` receives the subject, not the request, so a voter whose applicability depends on the requester has to say `true` here and abstain there.

## Always give a reason

The `reason` is the only thing that survives the decision. It is what the profiler panel shows, what a test assertion matches on, and what tells a developer six months later why the door was closed.

A reason is not a message for the end user. A denial reaching an HTTP response is a bare `403`: the diagnostic is deliberately withheld from the response and available to the profiler, the log and the tests. If you want the visitor to read something, say so with the `message` of an [access policy](../pure-php/access-policies.md).

## Weights

An outcome carries a weight, which defaults to `1`:

```php
AccessOutcome::deny('The account is suspended.', weight: 10);
```

Only the `majority` combining algorithm reads it. It lets a voter be given more say than the others without being given a veto. Under the three other algorithms the weight is ignored, so do not use it to try to make a voter authoritative: use `first_applicable` and voter order, or `deny_overrides`, both of which say what they mean.

## The voters that ship

| Service | What it decides |
|---|---|
| `access_control.voter.role` | Attributes that start with the role prefix, `ROLE_` by default, against the roles the requester holds, expanded through the role hierarchy |
| `access_control.voter.authenticated` | The six authentication states: `IS_AUTHENTICATED_FULLY`, `IS_AUTHENTICATED_REMEMBERED`, `IS_AUTHENTICATED`, `IS_IMPERSONATOR`, `IS_REMEMBERED` and `PUBLIC_ACCESS` |
| `access_control.voter.closure` | An attribute given as a `Closure`, called with the request |
| `ExpressionVoter` | An attribute given as an `Expression`, when `symfony/expression-language` is installed |

`RoleVoter` reads roles from a Symfony token when it gets one, and otherwise from any requester implementing `UserWithRoleInterface` or simply carrying a `getRoles()` method. That contract is this component's own: the notion of role is meant to leave Security, so nothing here types against Security's interfaces.

A role name and an authentication state are two different vocabularies, read by two different voters. `ROLE_PREVIOUS_ADMIN` is a role, matched by its prefix; `IS_IMPERSONATOR` is a state, and `RoleVoter` abstains on it.

## Reusing voters written for Symfony Security

They keep working, unchanged. `VoterAdapter` wraps a `Symfony\Component\Security\Core\Authorization\Voter\VoterInterface` so it answers questions asked here, and the bundle wires every one of them for you. See [Coming From Security](../migration/from-security.md).
