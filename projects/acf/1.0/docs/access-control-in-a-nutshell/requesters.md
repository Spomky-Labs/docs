# Requesters and actors

The requester is who asks. It is typed `mixed`, and that is the point: this component decides without a token, without a user, and without a firewall.

## Anything can be a requester

```php
$accessControlManager->decide(new AccessRequest($token, 'EDIT', $post));
$accessControlManager->decide(new AccessRequest($apiKey, 'EDIT', $post));
$accessControlManager->decide(new AccessRequest($serviceAccount, 'EDIT', $post));
$accessControlManager->decide(new AccessRequest(null, 'PUBLIC_ACCESS'));
```

A voter that does not understand a requester abstains. Nothing raises, nothing denies by accident.

## Roles without Symfony Security

`RoleVoter` reads roles from a Symfony `TokenInterface` when it gets one. Otherwise it reads them from any requester implementing this component's own contract:

```php
use AccessControl\Voter\RBAC\UserWithRoleInterface;

final readonly class ServiceAccount implements UserWithRoleInterface
{
    /**
     * @return list<string>
     */
    public function getRoles(): array
    {
        return ['ROLE_IMPORTER'];
    }
}
```

An object that merely carries a `getRoles()` method works too, without implementing anything. That contract is deliberately this component's own: the notion of role is meant to leave Security, so nothing here types against Security's interface.

Roles are expanded through the [role hierarchy](../symfony-bundle/configuration.md#role-hierarchy) before being matched, so holding `ROLE_ADMIN` answers a question about `ROLE_USER` when the hierarchy says so.

## Who is really asking: the actor

Two situations share one shape under opposite names:

* an administrator **impersonating** a user, who granted them nothing,
* an agent a user has **authorised** to act for them.

The word that covers both is the one RFC 8693 uses: the **requester** is who the access is asked for, the **actor** is who is really asking.

```php
use AccessControl\Requester\DelegatedRequesterInterface;

final readonly class ActingFor implements DelegatedRequesterInterface
{
    public function __construct(
        private User $onBehalfOf,
        private User $agent,
    ) {
    }

    public function getActor(): mixed
    {
        return $this->agent;
    }
}
```

`Actor::of($requester)` hands back the actor, or `null` when nobody else is acting, which is the ordinary case. `Actor::isActedFor($requester)` answers the same question as a boolean, and is what makes `IS_IMPERSONATOR` decidable where there is no token at all.

It is a contract on the requester rather than a wrapper around it, deliberately: wrapping would hide the requester from every voter that reads its type.

Symfony's `SwitchUserToken` is understood without implementing anything: `Actor::of()` returns its original token. The reference is soft, as everywhere here, so the component stands alone when `symfony/security-core` is absent.

## Telling the component who is asking

Entry points do not receive a requester as an argument; they ask a `RequesterProviderInterface` for it.

```php
interface RequesterProviderInterface
{
    public function getRequester(): mixed;
}
```

Two implementations ship:

| Service | What it hands over |
|---|---|
| `access_control.requester_provider.static` | Always the same requester, typically a service account in a console context. The default. |
| `TokenStorageRequesterProvider` | The token currently in Symfony's token storage. Wired for you when Security is installed. |

Replace the `access_control.requester_provider` alias to point the whole application at your own:

```yaml
services:
    App\Security\CurrentRequesterProvider: ~

    access_control.requester_provider:
        alias: App\Security\CurrentRequesterProvider
```

This is what makes `#[AccessPolicy]`, the URL rules, the Twig functions and the console guards work in an application that has no Security at all: they all ask the same provider.

## Asking on behalf of somebody else

`RequesterBoundChecker` is the service that binds the current requester to a question, and is what `is_granted()` and the controller helpers go through.

```php
$checker->isGranted('EDIT', $post);   // bool
$checker->decide('EDIT', $post);      // the full AccessDecision
```

To ask about a requester that is not the current one, build the request yourself and hand it to the manager:

```php
$accessControlManager->decide(new AccessRequest($otherUser, 'EDIT', $post));
```
