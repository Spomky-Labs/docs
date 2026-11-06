# Configuration

Everything lives under one root key, `access_control`. **There is no `enabled` flag: registering the bundle is the opt-in.**

```yaml
# config/packages/access_control.yaml
access_control:
    default_strategy: permit_overrides
    allow_if_all_abstain: false
    allow_if_equal_granted_denied: true
    role_prefix: 'ROLE_'
```

## The decision settings

| Key | Default | |
|---|---|---|
| `default_strategy` | `permit_overrides` | The combining algorithm applied when a request names none. One of `permit_overrides`, `deny_overrides`, `majority`, `first_applicable`. |
| `allow_if_all_abstain` | `false` | What to answer when no voter had anything to say. |
| `allow_if_equal_granted_denied` | `true` | Whether `majority` grants when both sides weigh the same. |
| `role_prefix` | `ROLE_` | The prefix an attribute must carry to be read as a role. |

See [Combining Algorithms](../access-control-in-a-nutshell/combining-algorithms.md) for what each one does and for the Security names they correspond to.

`role_prefix` is the one setting with no equivalent in SecurityBundle, where `'ROLE_'` comes from a constructor default and can only be changed by redefining the service.

## If your application has Security, declare it there

An application with SecurityBundle keeps declaring these under `security.access_decision_manager`, and the bridge reads them. **Do not declare the same thing on both keys.**

Saying it twice does not silently pick one: the bundle raises at compile time on two algorithms named at once, on two contradictory values of `allow_if_all_abstain`, on two role hierarchies, and on two sets of URL rules. A build that stops is the point; access rules that quietly loosen are what this avoids.

## Role hierarchy

```yaml
access_control:
    role_hierarchy:
        ROLE_ADMIN: [ROLE_USER]
        ROLE_SUPER_ADMIN: [ROLE_ADMIN, ROLE_ALLOWED_TO_SWITCH]
```

The shape is that of `security.role_hierarchy`, down to the normalisations, so a hierarchy reads the same whichever key declares it and moves across without being rewritten.

**Declare it here only when the application has no Security.** With SecurityBundle installed, keep it in `security.yaml`: the bridge points this component's service at `security.role_hierarchy`, so one tree serves both stacks and an application that replaced that service is honoured here too. Declaring it on both keys raises at compile time.

The adaptation goes that way round on purpose. Putting this component's implementation behind `security.role_hierarchy` would break every application typed against Security's interface, which this component does not implement and must not, the notion of role being on its way out of there.

## URL rules

```yaml
access_control:
    rules:
        - { path: ^/admin, roles: [ROLE_ADMIN] }
        - { path: ^/api, requires_channel: https }
```

The options are those of `security.access_control`. The key is `rules` rather than `access_control`, which would have read as `access_control.access_control`.

They are not a duplicate of Security's, and the difference matters. See [URL Rules](url-rules.md).

## Services you may want to replace

| Service | What it does |
|---|---|
| `access_control.requester_provider` | Tells the component who is currently asking. An alias, pointing at the static provider by default and at the token storage when Security is installed. |
| `access_control.manager` | The manager. Aliased from `AccessControlManagerInterface`. |
| `access_control.checker` | Binds the current requester to a question. Aliased from `RequesterBoundChecker`. |
| `access_control.role_hierarchy` | Aliased from `RoleHierarchyInterface`. |

Replacing the requester provider is what makes the whole component work in an application with no Security at all: every entry point asks that one service. See [Requesters and Actors](../access-control-in-a-nutshell/requesters.md#telling-the-component-who-is-asking).

## Registering your own pieces

Implementing the interface is enough; autoconfiguration does the rest.

| Interface | Tag |
|---|---|
| `AccessControl\VoterInterface` | `access_control.voter` |
| `AccessControl\Strategy\StrategyInterface` | `access_control.strategy` |
| `AccessControl\Handler\AccessPolicyHandlerInterface` | `access_control.policy_handler` |

```bash
bin/console debug:container --tag=access_control.voter
```

`debug:container` may report these three tags as unused. That is cosmetic: FrameworkBundle's list of known tags does not include them, this bundle living outside the Symfony repository.
