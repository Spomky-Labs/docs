# Client override policy

!!! info

    **New in v5.3.0**

The Client Override Policy provides granular control over which WebAuthn options clients can override via request parameters. This allows you to define strict server-side defaults while optionally allowing clients to customize specific fields within constrained boundaries.

!!! warning

    **Deprecated in v5.4.0:** the `webauthn.client_override_policy` YAML node is removed in 6.0.0, together with the profiles it applies to. When you build options through the [Options Helpers](../options-helpers.md), attach the policy with `withClientOverrides(...)` and use the typed `ClientOverridePolicy::fromRules()` factory documented under *Client overrides* on that page. The YAML node keeps working in 5.4.

## Overview

When building WebAuthn options from a profile, the server uses configured defaults. With the Client Override Policy, you can control whether HTTP request parameters can override these defaults and which values are acceptable.

Each policy field has:
* **enabled**: Whether the client can override this field at all
* **allowed_values**: An optional list of accepted values (if omitted, all valid values are allowed)

## Helper-side, typed API (5.4)

`ClientOverridePolicy::fromRules()` and `ClientOverrideRule` give you a named-argument, typed alternative to the YAML / nested-array form. Both shapes are first-class: pick whichever fits your use case best.

```php
use Webauthn\Bundle\Policy\ClientOverridePolicy;
use Webauthn\Bundle\Policy\ClientOverrideRule;

$policy = ClientOverridePolicy::fromRules(
    userVerification:        ClientOverrideRule::restrictTo(['preferred', 'required']),
    authenticatorAttachment: ClientOverrideRule::restrictTo(['platform', 'cross-platform']),
    residentKey:             ClientOverrideRule::any(),
    extensions:              ClientOverrideRule::any(),
);

return $this->options
    ->forCreation('example.com', $this->guesser)
    ->withClientOverrides($policy)
    ->build($request);
```

* Pass `null` (the default) for fields the client must NOT be able to override. A policy built in PHP has no defaults: the defaults listed below only apply to the YAML node.
* `ClientOverrideRule::any()` accepts any value the client submits.
* `ClientOverrideRule::restrictTo($allowedValues)` restricts to a list.

## Configuration

The example below shows every field with an explicit value. You only need to declare the fields you want to change, the rest fall back to the [defaults](#configurable-fields) listed in the next section. The `client_override_policy` node sits at the root of the configuration and applies to every creation and request profile.

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    client_override_policy:
        user_verification:
            enabled: true
            allowed_values: ['required', 'preferred']
        authenticator_attachment:
            enabled: true
            allowed_values: ['platform', 'cross-platform']
        resident_key:
            enabled: true
            allowed_values: ['required', 'preferred', 'discouraged']
        attestation_conveyance:
            enabled: true
            allowed_values: ['indirect', 'direct', 'enterprise']
        extensions:
            enabled: true
        mediation:
            enabled: false   # disabled by default; opt-in
            allowed_values: ['default', 'conditional']
```

## Configurable fields

| Field | Default | Default Allowed Values | Description |
|-------|---------|------------------------|-------------|
| `user_verification` | **disabled** | `required`, `preferred` | Whether the client can request a specific user verification level. Disabled by default to prevent downgrade attacks; `discouraged` is excluded from the defaults even when you enable the override. |
| `authenticator_attachment` | enabled | `platform`, `cross-platform` | Whether the client can request a specific authenticator type |
| `resident_key` | enabled | `required`, `preferred`, `discouraged` | Whether the client can request resident key behavior |
| `attestation_conveyance` | enabled | `indirect`, `direct`, `enterprise` | Whether the client can request attestation preference. `none` is left out of the defaults since v5.3.13, see below. |
| `extensions` | enabled | N/A | Whether the client can add extensions to those of the profile. The extensions of the profile are never removed nor replaced. |
| `mediation` | **disabled** | `default`, `conditional` | Whether the client can request the [Conditional Create](../../pure-php/advanced-behaviours/conditional-create.md) flow (auto-register), opt-in. |

!!! info

    **Changed in v5.4.0:** the client can no longer remove nor replace the extensions of the profile. The extensions it sends are added to them, and an extension the profile already sets keeps the value of the profile. Until then, the extensions sent by the client replaced those of the profile: a client that posted `{"extensions": {}}` received options without any of them.

!!! warning

    **Why `user_verification` is disabled by default.** Allowing a client to override the user verification requirement makes it possible to request `discouraged` against a profile that mandates `required`, which silently weakens the security guarantee. If you enable this override, keep `discouraged` out of `allowed_values` and **always re-check the `UV` flag at the application layer** — see [User Verification](../../webauthn-in-a-nutshell/user-verification.md#checking-the-uv-flag).

!!! danger

    **Changed in v5.3.13:** `none` is no longer in the default allowed values of `attestation_conveyance` ([GHSA-473f-pfcw-p4h2](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-473f-pfcw-p4h2)). Until then, a client could ask for `none` against a profile that requests an attestation: the stored options then said that no attestation was requested, the metadata checks (status reports, certificate chain, attestation type) were skipped, and the credential record still stored the attestation type, the trust path and the AAGUID sent by the authenticator.

    A client that asks for `none` now gets the conveyance of the profile. `indirect`, `direct` and `enterprise` can still be requested, and each of them is verified. To let the client waive the attestation again, list `none` explicitly, and do not rely on the attestation of the resulting credential records:

    ```yaml title="config/packages/webauthn.yaml"
    webauthn:
        client_override_policy:
            attestation_conveyance:
                allowed_values: ['none', 'indirect', 'direct', 'enterprise']
    ```

!!! danger

    **Changed in v5.3.15:** overriding one member of `authenticatorSelection` keeps the other members of the profile ([GHSA-2989-5cjp-qc2p](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-2989-5cjp-qc2p)). Until then, a request that carried `authenticatorAttachment` or `residentKey`, two members the client can override by default, made the bundle rebuild the criteria from the client values alone: `userVerification` fell back to `preferred`, and `residentKey` to the client value or to no value at all. The stored options then said `preferred`, so a profile configured with `user_verification: required` accepted a credential created without user verification. The hardening of v5.3.1 ([GHSA-h4fw-6r7f-w494](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-h4fw-6r7f-w494)) only covered the `userVerification` member.

    Each member now keeps the value of the profile, unless the client sent a value that the policy allows for that very member. On a profile that requires user verification, a registration without user verification is refused whatever the client sends. On earlier versions, disable the two overrides to get the same result:

    ```yaml title="config/packages/webauthn.yaml"
    webauthn:
        client_override_policy:
            authenticator_attachment:
                enabled: false
            resident_key:
                enabled: false
    ```

## Examples

### Restrict to platform authenticators only

Force platform authenticators (like Touch ID, Windows Hello) and prevent clients from requesting cross-platform authenticators:

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    creation_profiles:
        passkeys_only:
            rp:
                id: 'example.com'
            authenticator_selection_criteria:
                authenticator_attachment: platform
    client_override_policy:
        authenticator_attachment:
            enabled: false  # Client cannot change this
```

### Lock down all options

For high-security scenarios, disable all client overrides:

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    creation_profiles:
        high_security:
            rp:
                id: 'example.com'
            authenticator_selection_criteria:
                user_verification: required
                require_resident_key: true
    client_override_policy:
        user_verification:
            enabled: false
        authenticator_attachment:
            enabled: false
        resident_key:
            enabled: false
        attestation_conveyance:
            enabled: false
        extensions:
            enabled: false
```

### Allow only specific verification levels

Allow the client to choose between `required` and `preferred`, but not `discouraged`:

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    client_override_policy:
        user_verification:
            enabled: true
            allowed_values: ['required', 'preferred']
```

### Opt-in conditional create from the client

Conditional mediation is one of the two overrides **disabled by default**, with `user_verification`. Enable it if you want the JavaScript client to request the [Conditional Create](../../pure-php/advanced-behaviours/conditional-create.md) flow without the profile being permanently configured for it:

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    client_override_policy:
        mediation:
            enabled: true
            allowed_values: ['default', 'conditional']
```

## How it works

The `ClientOverridePolicy` class determines the effective value for each field:

1. If no request value is provided, the profile default is used
2. If the override is disabled for that field, the profile default is used
3. If the request value is not in the `allowed_values` list, the profile default is used
4. Otherwise, the request value is used

The members of `authenticatorSelection` (`user_verification`, `authenticator_attachment` and `resident_key`) go through these rules one by one: a client that overrides one of them leaves the others to the profile. Until v5.3.15, overriding one member reset the others, see the warning above. The [options helpers](../options-helpers.md#behaviour) apply the same rule to the criteria set with `withAuthenticatorSelectionCriteria()`.

This ensures that the server always maintains control over the final options, while allowing controlled flexibility for client-side customization.

## See also

* [Configuration References](../configuration-references.md) - Full bundle configuration
* [Authenticator Selection Criteria](authenticator-selection-criteria.md) - Selection criteria details
* [User Verification](user-verification.md) - User verification options
