# User registration

The Symfony UX WebAuthn package provides Stimulus controllers to simplify the registration of new authenticators. This page explains how to register a new user with WebAuthn or add authenticators to an existing user account.

## New user registration

When registering a new user, you need to collect basic information (username, display name) and then register their first authenticator.

### Registration form

Your registration form needs:
1. A **username field** for the user's identifier
2. A **display name field** (optional, can default to username)
3. A **hidden field** for the attestation response

```twig title="templates/registration/register.html.twig" linenums="1"
<form
    action="{{ path('app_register') }}"
    method="post"
    {{ stimulus_controller('@web-auth/webauthn-stimulus',
        {
            creationOptionsUrl: path('webauthn.controller.creation.request.new_user'),
            creationResultField: 'input[name="attestation"]'
        }
    ) }}
>
    <label for="username">Username</label>
    <input
        type="text"
        id="username"
        name="username"
        required
        autocomplete="username webauthn"
    >

    <label for="displayName">Display Name</label>
    <input
        type="text"
        id="displayName"
        name="displayName"
        placeholder="John Doe"
    >

    <input type="hidden" id="attestation" name="attestation">

    <button
        type="submit"
        {{ stimulus_action('@web-auth/webauthn-stimulus', 'signup') }}
    >
        Register with Passkey
    </button>
</form>
```

### Bundle configuration

Configure the bundle to handle new user registration:

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    credential_repository: 'App\Repository\WebauthnCredentialRepository'
    user_repository: 'App\Repository\UserRepository'

    controllers:
        enabled: true
        creation:
            new_user:
                options_path: '/register/webauthn/options'
                result_path: '/register/webauthn'
                user_entity_guesser: 'App\Guesser\NewUserEntityGuesser'
```

### User entity guesser

Create a guesser to handle new user registration:

```php linenums="1"
<?php

declare(strict_types=1);

namespace App\Guesser;

use Symfony\Component\HttpFoundation\Request;
use Webauthn\Bundle\Security\Guesser\UserEntityGuesser;
use Webauthn\PublicKeyCredentialUserEntity;

final class NewUserEntityGuesser implements UserEntityGuesser
{
    public function findUserEntity(Request $request): PublicKeyCredentialUserEntity
    {
        $username = $request->request->get('username');
        $displayName = $request->request->get('displayName', $username);

        // Generate a unique user ID (64 bytes recommended)
        $userHandle = random_bytes(64);

        return PublicKeyCredentialUserEntity::create(
            $username,
            $userHandle,
            $displayName
        );
    }
}
```

!!! info

    After successful registration, save both the user entity and the credential source to your database. The controller automatically validates the attestation response.

## Adding authenticators to existing users

Existing users can register additional authenticators (backup keys, different devices).

### Add authenticator form

```twig title="templates/security/add_authenticator.html.twig" linenums="1"
<form
    action="{{ path('app_add_authenticator') }}"
    method="post"
    {{ stimulus_controller('@web-auth/webauthn-stimulus',
        {
            creationOptionsUrl: path('webauthn.controller.creation.request.add_device'),
            creationResultField: 'input[name="attestation"]'
        }
    ) }}
>
    <input type="hidden" id="attestation" name="attestation">

    <button
        type="submit"
        {{ stimulus_action('@web-auth/webauthn-stimulus', 'signup') }}
    >
        Add New Authenticator
    </button>
</form>
```

### Configuration for existing users

```yaml title="config/packages/webauthn.yaml" linenums="1"
webauthn:
    controllers:
        enabled: true
        creation:
            add_device:
                options_path: '/devices/add/options'
                result_path: '/devices/add'
                user_entity_guesser: 'Webauthn\Bundle\Security\Guesser\CurrentUserEntityGuesser'
```

!!! success

    The `CurrentUserEntityGuesser` automatically retrieves the currently authenticated user from the Symfony security context. No custom guesser needed!

## Stimulus controller options

The registration controller accepts the following options:

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `creationOptionsUrl` | string | Yes | URL to fetch credential creation options |
| `creationResultField` | string | Yes | CSS selector for the hidden attestation field |

The combined controller has no `autoRegister` option: Conditional Create is only available on the [dedicated registration controller](#conditional-create).

## Dedicated registration controller

!!! info

    **New in v5.3.0:** A dedicated registration controller is available alongside the combined controller.

The dedicated `registration-controller` provides a focused controller for credential registration with enhanced features like conditional create support.

### Basic usage

```twig title="templates/registration/register.html.twig" linenums="1"
<form
    action="{{ path('app_register') }}"
    method="post"
    {{ stimulus_controller('@web-auth/webauthn-stimulus/registration', {
        optionsUrl: path('webauthn.controller.creation.request.new_user'),
        resultUrl: path('app_register'),
        submitViaForm: true
    }) }}
>
    <input
        type="text"
        name="username"
        required
        {{ stimulus_target('@web-auth/webauthn-stimulus/registration', 'username') }}
    >
    <input
        type="hidden"
        name="attestation"
        {{ stimulus_target('@web-auth/webauthn-stimulus/registration', 'result') }}
    >

    <button
        type="button"
        {{ stimulus_action('@web-auth/webauthn-stimulus/registration', 'register') }}
    >
        Register with Passkey
    </button>
</form>
```

### Registration controller options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `optionsUrl` | string | `/registration/options` | URL to fetch creation options |
| `resultUrl` | string | `/registration/verify` | URL to submit the attestation response |
| `submitViaForm` | boolean | `false` | Submit via form instead of fetch |
| `successRedirectUri` | string | - | URL to redirect after successful registration |
| `autoRegister` | boolean | `false` | Request a Conditional Create (`mediation: 'conditional'`) when the `register` action runs |

### Conditional Create

`autoRegister: true` does not start anything when the page loads: the controller only dispatches its `webauthn:registration:connect` event there, and the ceremony still starts when the `register` action runs. The option turns that ceremony into a Conditional Create (`mediation: 'conditional'`), so the browser may create the passkey without prompting a user who has just signed in with a saved password.

```twig linenums="1"
{{ stimulus_controller('@web-auth/webauthn-stimulus/registration', {
    optionsUrl: path('webauthn.controller.creation.request.new_user'),
    resultUrl: path('app_register'),
    autoRegister: true
}) }}
```

The creation options must be built for conditional mediation on the server side too, otherwise the user presence check can reject the response. See [Conditional Create](../pure-php/advanced-behaviours/conditional-create.md).

### Registration controller targets

| Target | Description |
|--------|-------------|
| `username` | Input field for the username |
| `attestation` | Select field for attestation preference |
| `residentKey` | Select field for resident key preference |
| `userVerification` | Select field for user verification preference |
| `authenticatorAttachment` | Select field for authenticator attachment preference |
| `result` | Hidden input for the attestation response |

### Registration controller events

The controller dispatches the following events on its element. They bubble, so a listener on `document` receives them. When `submitViaForm` is enabled and the controller has a `result` target, the form is submitted instead of the `verify` request, so the three `verify` events are not dispatched.

| Event | Detail | Dispatched |
|-------|--------|------------|
| `webauthn:registration:connect` | `optionsUrl`, `resultUrl`, `supportsPlatformAuthenticator` | When the controller connects |
| `webauthn:unsupported` | none | When the `register` action runs in a browser without WebAuthn support |
| `webauthn:registration:options:request` | `data` | Before the options are requested from `optionsUrl` |
| `webauthn:registration:options:success` | `options` | When the options are received |
| `webauthn:registration:options:error` | `response` or `error` | When the options request fails |
| `webauthn:registration:credential` | `credential` | When the authenticator answers, before anything is sent |
| `webauthn:registration:verify:request` | `credential` | Before the credential is sent to `resultUrl`, as it is sent: without `prf.results` since v5.3.15 |
| `webauthn:registration:verify:success` | `result` | When `resultUrl` accepts the credential |
| `webauthn:registration:verify:error` | `response` or `error` | When `resultUrl` refuses the credential or cannot be reached |
| `webauthn:registration:error` | `error`, plus `code` and `name` for a WebAuthn error | When the ceremony fails |

When the options carry the `prf` extension, the PRF results are on the credential of the `webauthn:registration:credential` event and are not sent to the server. See [PRF results](user-authentication.md#prf-results), including the change of v5.3.15.

## Error handling

Handle the registration outcome in your custom event listeners. A refusal of the server comes with the `verify:error` event, a failure of the ceremony itself with the `error` event:

```javascript linenums="1"
document.addEventListener('webauthn:registration:error', (event) => {
    console.error('Registration failed:', event.detail.error);
    alert('Could not register authenticator: ' + event.detail.error.message);
});

document.addEventListener('webauthn:registration:verify:error', (event) => {
    console.error('The server refused the authenticator:', event.detail.response ?? event.detail.error);
});

document.addEventListener('webauthn:registration:verify:success', (event) => {
    console.log('Registration successful!', event.detail.result);
});
```

## See also

* [User Authentication](user-authentication.md) - Authenticate users with registered authenticators
* [Additional Authenticators](additional-authenticators.md) - Manage multiple authenticators
* [Bundle Configuration](../symfony-bundle/configuration-references.md) - Complete configuration reference
