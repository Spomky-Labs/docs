# User authentication

With the version 5.2 of the bundle, the login process is very similar to the username/password login.

First, your login form needs a username field. This field is not required ([usernameless authentication](../pure-php/advanced-behaviours/authentication-without-username.md)). You can indicate the autocomplete method is `webauthn`; this helps the browser understand the purpose of this field.

Second, a hidden field `assertion` where the authenticator assertion will be placed is required. The name `assertion` can be changed, but shall be the same declared in the next step.

```twig
<form action="{{ path('app_login') }}" method="post">
    <label for="username">Username</label>
    <input name="username" type="text" id="username" placeholder="Type your username here" autocomplete="username webauthn">
    <input type="hidden" id="assertion" name="assertion">

    <button type="submit">
        Sign in
    </button>
</form>
```

You now have only two Twig functions to call: `stimulus_controller` and `stimulus_action`.&#x20;

* The first one is placed on the `form` level;
* The latter on the `button`.

The Stimulus Controller should be configured to fit your needs. The route names used below are automatically created by the bundle configuration.

The `requestResultField` parameter corresponds to the selector to the hidden field added above. Please use the corresponding field name.

```twig
<form action={{ path('app_login') }} method="post"
    {{ stimulus_controller('@web-auth/webauthn-stimulus',
        {
             requestOptionsUrl: path('webauthn.controller.request.request.login'),
             requestResultField: 'input[name="assertion"]'
        }
    ) }}
>
    <label for="username">Username</label>
    <input name="username" type="text" id="username" placeholder="Type your username here" autocomplete="username webauthn">
    <input type="hidden" id="assertion" name="assertion">

    <button
        type="submit"
        {{ stimulus_action('@web-auth/webauthn-stimulus', 'signin') }}
    >
        Sign in
    </button>
</form>

```

### Redirection after login

The behavior after the login is managed by your Symfony Security Authenticator.

### Browser autofill

When authenticators are available on the device and the browser is aware of them, you can simplify the way users will sign in. When this feature is enabled, the user will see the list of available authenticators when focusing on the username field. Selecting an account in the list will automatically perform the authentication actions. There is a simple option to enable this feature:

```twig
{{ stimulus_controller('@web-auth/webauthn-stimulus',
    {
        useBrowserAutofill: true,
        requestOptionsUrl: path('webauthn.controller.request.request.login'),
        requestResultField: 'input[name="assertion"]'
    }
) }}
```

## Dedicated authentication controller

!!! info

    **New in v5.3.0:** The Stimulus package now provides dedicated controllers for authentication and registration, in addition to the combined controller.

The new `authentication-controller` provides a focused controller specifically for sign-in flows, with built-in support for conditional UI and better error handling.

### Basic usage

```twig title="templates/security/login.html.twig" linenums="1"
<form
    action="{{ path('app_login') }}"
    method="post"
    {{ stimulus_controller('@web-auth/webauthn-stimulus/authentication', {
        optionsUrl: path('webauthn.controller.request.request.login'),
        resultUrl: path('app_login'),
        submitViaForm: true
    }) }}
>
    <input
        type="text"
        name="username"
        autocomplete="username webauthn"
        {{ stimulus_target('@web-auth/webauthn-stimulus/authentication', 'username') }}
    >
    <input
        type="hidden"
        name="assertion"
        {{ stimulus_target('@web-auth/webauthn-stimulus/authentication', 'result') }}
    >

    <button
        type="button"
        {{ stimulus_action('@web-auth/webauthn-stimulus/authentication', 'authenticate') }}
    >
        Sign in
    </button>
</form>
```

### Conditional UI (autofill)

The dedicated controller supports conditional UI natively:

```twig linenums="1"
{{ stimulus_controller('@web-auth/webauthn-stimulus/authentication', {
    optionsUrl: path('webauthn.controller.request.request.login'),
    resultUrl: path('app_login'),
    submitViaForm: true,
    conditionalUi: true
}) }}
```

!!! info

    **Changed in v5.4.0:** on connect, the controller reads the client capabilities with `PublicKeyCredential.getClientCapabilities()` and starts the conditional UI only when `conditionalGet` is `true`. On the browsers that do not ship that method yet, the capability is derived from SimpleWebAuthn's `browserSupportsWebAuthnAutofill()`. When the capability is missing, `conditionalUi: true` starts nothing and the user signs in with the `authenticate` action.

The capability map is exposed as `capabilities` in the detail of the `webauthn:authentication:connect` event (and of `webauthn:registration:connect` for the registration controller), next to `optionsUrl`, `resultUrl` and `supportsPlatformAuthenticator`. The events bubble, so a listener on `document` receives them:

```javascript linenums="1"
document.addEventListener('webauthn:authentication:connect', (event) => {
    const { capabilities } = event.detail;
    if (capabilities.conditionalGet !== true) {
        // Show a "Sign in with a passkey" button instead of relying on autofill
    }
});
```

### Authentication controller options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `optionsUrl` | string | `/authentication/options` | URL to fetch assertion options |
| `resultUrl` | string | `/authentication/verify` | URL to submit the assertion response |
| `submitViaForm` | boolean | `false` | Submit via form instead of fetch |
| `successRedirectUri` | string | - | URL to redirect after successful auth |
| `conditionalUi` | boolean | `false` | Enable conditional UI (autofill) on connect, when the browser reports the `conditionalGet` capability |
| `verifyAutofillInput` | boolean | `true` | Verify autofill input fields exist |

### Authentication controller targets

| Target | Description |
|--------|-------------|
| `username` | Input field for the username |
| `userVerification` | Input field for user verification preference |
| `result` | Hidden input for the assertion response |

### Authentication controller events

The controller dispatches the following events on its element. They bubble, so a listener on `document` receives them. When `submitViaForm` is enabled and the controller has a `result` target, the form is submitted instead of the `verify` request, so the three `verify` events are not dispatched.

| Event | Detail | Dispatched |
|-------|--------|------------|
| `webauthn:authentication:connect` | `optionsUrl`, `resultUrl`, `supportsPlatformAuthenticator`, `capabilities` | When the controller connects |
| `webauthn:unsupported` | none | When the `authenticate` action runs in a browser without WebAuthn support |
| `webauthn:authentication:options:request` | `data` | Before the options are requested from `optionsUrl` |
| `webauthn:authentication:options:success` | `options` | When the options are received |
| `webauthn:authentication:options:error` | `response` or `error` | When the options request fails |
| `webauthn:authentication:credential` | `credential` | When the authenticator answers, before anything is sent |
| `webauthn:authentication:verify:request` | `credential` | Before the credential is sent to `resultUrl`, as it is sent: without `prf.results` since v5.3.15 |
| `webauthn:authentication:verify:success` | `result` | When `resultUrl` accepts the credential |
| `webauthn:authentication:verify:error` | `response` or `error` | When `resultUrl` refuses the credential or cannot be reached |
| `webauthn:authentication:error` | `error`, plus `code` and `name` for a WebAuthn error | When the ceremony fails |

#### PRF results

When the options carry the `prf` extension, the controller encodes `clientExtensionResults.prf.results.first` (and `second`) as base64url strings on the credential of the `webauthn:authentication:credential` event, and leaves them out of what it sends to the server. Read them from that event, see [PRF extension](../pure-php/advanced-behaviours/prf-extension.md#stimulus-integration).
