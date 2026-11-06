# URL rules

Rules that guard parts of the site by path, host, port, IP, route, method or expression. They are matched in declaration order, the first match winning.

```yaml
access_control:
    rules:
        - { path: ^/admin, roles: [ROLE_ADMIN] }
        - { path: ^/profile, roles: [IS_AUTHENTICATED_FULLY] }
        - { path: ^/api, requires_channel: https }
```

## The options

They are those of `security.access_control`, with the same normalisations, so a rule moves across without being rewritten.

| Option | |
|---|---|
| `path` | A regular expression, in the urldecoded format: `^/path to resource/` |
| `host`, `port`, `ips`, `methods`, `route` | The obvious matchers |
| `attributes` | Request attributes to match, `_route` among them |
| `request_matcher` | A service id, which rules out every other matching option above |
| `roles` | The attributes to require. Any one granting is enough |
| `allow_if` | An expression. Requires `symfony/expression-language` |
| `requires_channel` | `http` or `https` |

`roles` and `allow_if` given together are combined as `AtLeastOneOf`: either one granting lets the request through. Naming `request_matcher` alongside `path`, `host`, `port`, `ips`, `methods`, `attributes` or `route` raises, rather than quietly ignoring one of them. A rule with nothing in it raises too, which catches the stray `-` in YAML.

## They are not a duplicate of Security's

The two sections are identical option for option, but their **scopes differ**, and this is the part worth knowing:

| | `security.access_control` | `access_control.rules` |
|---|---|---|
| Where it applies | Inside a firewall only | Everywhere |

Security's rules feed `security.access_map`, consumed by a listener that is a link in each firewall's chain. **A path outside every firewall can only be guarded here.**

## When both cover the same path

Both apply. The firewall runs first, at `kernel.request` priority 8, and this component's listener at 7. The result is the **intersection** of the permissions.

A rule added here can therefore only tighten, never loosen. That is fail-closed and not dangerous, but it is silent: **moving a rule from one key to the other without deleting the original leaves you with both**, and the permissions of neither.

Declaring rules on both keys at once raises at compile time. What does not raise is the case above, where a rule is *moved* rather than duplicated.

## `requires_channel` is enforced once

This is the precision that costs an afternoon if you miss it:

* with a firewall covering the path, **the firewall enforces it**,
* without one, **this component's `ChannelListener` does**,
* never both.

When no rule declares `requires_channel`, that listener is not even registered.

## Roles, and the attributes you can put there

Despite the name, `roles` takes attributes, not only roles. Anything a voter understands works: a role, an authentication state such as `IS_AUTHENTICATED_FULLY`, or an attribute of your own that a voter answers.

```yaml
access_control:
    rules:
        - { path: ^/admin, roles: [ROLE_ADMIN] }
        - { path: ^/beta, roles: [FEATURE_BETA] }
        - { path: ^/reports, allow_if: "is_granted('VIEW_REPORTS') and request.getClientIp() matches '/^10\\./'" }
```

The name is Security's, kept so a `security.yaml` moves across unchanged.
