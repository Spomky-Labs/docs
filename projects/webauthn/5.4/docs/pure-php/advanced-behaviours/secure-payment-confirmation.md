# Secure payment confirmation (SPC)

!!! info

    **New in v5.4.0**

[Secure Payment Confirmation](https://www.w3.org/TR/secure-payment-confirmation/) is a W3C Web API that lets the relying party authenticate a payment with WebAuthn while having the user agent display the transaction details (amount, payee, instrument) in its own trusted UI. It is the building block recommended by EMV 3DS v2.3.1.1 §6.1.4.1.5 for FIDO-based SCA.

The framework ships SPC support out of the box: a `payment` extension, a dedicated client-data collector, an output checker for the browser-bound signature, and a Stimulus controller.

## How the pieces fit together

W3C SPC §5.1 splits the verification work in two — the framework wires both:

1. **`clientDataJSON.payment`** carries the transaction the user actually confirmed in the browser SPC dialog. It is signed by the authenticator and validated server-side by `PaymentClientDataCollector`, which compares each field (`rpId`, `topOrigin`, `total`, `instrument`, `payee*`) with the request options. This closes the threat of a compromised client substituting the amount the user signs.
2. **`clientExtensionResults.payment.browserBoundSignature`** carries the browser-bound signature. Its structural presence is enforced by `PaymentExtensionOutputChecker`. Cryptographic verification against the `BrowserBoundPublicKey` returned at registration is performed by `BrowserBoundSignatureVerifier`, wired into the assertion ceremony as `CheckBrowserBoundSignature`.

## Building a payment authentication request

Attach a `PaymentExtension` to your `PublicKeyCredentialRequestOptions`. The extension takes the rpId, the merchant top-level origin, the amount, the instrument and the payee fields:

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\AuthenticationExtensions\AuthenticationExtensions;
use Webauthn\AuthenticationExtensions\PaymentExtension;
use Webauthn\PublicKeyCredentialRequestOptions;
use Webauthn\SecurePaymentConfirmation\PaymentCredentialInstrument;
use Webauthn\SecurePaymentConfirmation\PaymentCurrencyAmount;

$amount = PaymentCurrencyAmount::create('EUR', '99.99');

$instrument = PaymentCredentialInstrument::create(
    displayName: 'Visa •••• 1234',
    icon: 'https://example.com/icons/visa.png',
);

$paymentExtension = PaymentExtension::authenticate(
    rpId: 'bank.example.com',
    topOrigin: 'https://merchant.example.com',
    total: $amount,
    instrument: $instrument,
    payeeName: 'Merchant Store',
    payeeOrigin: 'https://merchant.example.com',
);

$options = PublicKeyCredentialRequestOptions::create(
    challenge: random_bytes(32),
    rpId: 'bank.example.com',
    extensions: AuthenticationExtensions::create([$paymentExtension]),
);
```

For registration, use `PaymentExtension::register()` — the registration form of the extension only emits `isPayment: true`.

!!! danger

    Always derive the amount, instrument and payee fields from a server-side transaction record, **never** from request input. See [Security Model](#security-model) below.

## Validating the assertion

The Symfony bundle auto-registers `PaymentClientDataCollector` and `PaymentExtensionOutputChecker`, so a regular `AuthenticatorAssertionResponseValidator::check(...)` call performs full SPC validation:

```php linenums="1"
$credentialRecord = $authenticatorAssertionResponseValidator->check(
    credentialRecord: $storedCredentialRecord,
    authenticatorAssertionResponse: $publicKeyCredential->response,
    publicKeyCredentialRequestOptions: $storedOptions,
    host: 'bank.example.com',
    userHandle: $userId,
);
```

Pass the request options stored when the challenge was issued. Options rebuilt at verification time from a transaction record that has changed since no longer match what the user signed, and `PaymentClientDataCollector` rejects the assertion.

For pure PHP usage, wire the new pieces into the ceremony manager factory yourself:

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\AuthenticationExtensions\ExtensionOutputCheckerHandler;
use Webauthn\AuthenticationExtensions\PaymentExtensionOutputChecker;
use Webauthn\CeremonyStep\CeremonyStepManagerFactory;
use Webauthn\ClientDataCollector\ClientDataCollectorManager;
use Webauthn\ClientDataCollector\PaymentClientDataCollector;
use Webauthn\ClientDataCollector\WebauthnAuthenticationCollector;

$clientDataManager = new ClientDataCollectorManager([
    new WebauthnAuthenticationCollector(),
    new PaymentClientDataCollector($serializer),
]);

$extensionHandler = ExtensionOutputCheckerHandler::create();
$extensionHandler->add(new PaymentExtensionOutputChecker());

$factory = new CeremonyStepManagerFactory();
$factory->setClientDataCollectorManager($clientDataManager);
$factory->setExtensionOutputCheckerHandler($extensionHandler);
```

## Data structures

All value objects live under the `Webauthn\SecurePaymentConfirmation` namespace and validate their inputs in the constructor (ISO 4217 currencies, W3C decimal monetary regex, URL validation on origins, non-empty strings on names).

| Class | Purpose |
| --- | --- |
| `PaymentCurrencyAmount` | ISO 4217 currency + decimal value (`'EUR'`, `'99.99'`). |
| `PaymentCredentialInstrument` | `displayName`, `icon` (a URL), `iconMustBeShown` (`true` by default) and optional `details`. |
| `CollectedClientAdditionalPaymentData` | Mirrors what the browser signs in `clientDataJSON.payment`. |
| `CollectedClientPaymentData` | Top-level wrapper used by `PaymentClientDataCollector`. |
| `PaymentEntityLogo` | Optional `paymentEntitiesLogos[]` entry. |
| `BrowserBoundPublicKey` / `BrowserBoundSignature` | The COSE-encoded browser-bound key returned at registration and the signature returned at assertion. |
| `BrowserBoundSignatureVerifier` | CBOR-decodes the COSE key, looks up the matching `Cose\Algorithm\Signature\Signature` and verifies the signature against raw `clientDataJSON`. |

## Stimulus controller

The Stimulus package ships a `PaymentController` that extends `AuthenticationController`. It forwards the server-issued `payment` extension input to the user agent untouched and base64url-encodes `browserBoundSignature.signature` on the way back so the credential is JSON-transportable.

```html linenums="1"
<form data-controller="webauthn--payment"
      data-action="submit->webauthn--payment#authenticate"
      data-webauthn--payment-options-url-value="/payment/{{ transaction.id }}/options"
      data-webauthn--payment-result-url-value="/payment/{{ transaction.id }}/verify">

    <h2>Confirm payment</h2>
    <p>Amount: <strong>{{ transaction.formatted_amount }}</strong></p>
    <p>Merchant: <strong>{{ transaction.payee_name }}</strong></p>

    <input type="hidden" data-webauthn--payment-target="result">
    <button type="submit">Confirm</button>
</form>
```

The controller has no value for the transaction: it only posts the `username` and `userVerification` fields of the form to the options URL. The transaction ID is therefore part of the URL, and the server looks the transaction up from it.

The controller inherits every value, target, action and event from `AuthenticationController`. The defaults change to match the SPC convention:

| Value         | Default            |
| ------------- | ------------------ |
| `optionsUrl`  | `/payment/options` |
| `resultUrl`   | `/payment/verify`  |

!!! info

    The controller dispatches the same events as `AuthenticationController`, prefixed with `webauthn:authentication:`. Filter on the originating controller in your listeners.

## Security model

SPC is only as strong as the discipline of the relying party. Two rules matter above everything else:

1. **Never trust client-side payment data.** Amounts, payees and instruments must never travel through HTML attributes or JavaScript. Build the transaction server-side, store its details indexed by an opaque ID, and only pass that ID to the page. The Stimulus `PaymentController` sends no payment data at all: the ID is part of the options URL, and the server resolves the rest.
2. **Re-derive the `payment` extension from the database.** When the options endpoint is hit, fetch the transaction by the ID in its URL, verify it belongs to the authenticated user and is still pending, then build the `PaymentExtension` from the database row.

```php linenums="1"
#[Route('/payment/{transactionId}/options', methods: ['POST'])]
public function options(string $transactionId): JsonResponse
{
    $transaction = $this->transactionRepository->findOneBy([
        'id' => $transactionId,
        'userId' => $this->getUser()->getId(),
        'status' => 'pending',
    ]);

    if ($transaction === null || $transaction->isExpired()) {
        return new JsonResponse(['error' => 'Invalid transaction'], 400);
    }

    $paymentExtension = PaymentExtension::authenticate(
        rpId: 'bank.example.com',
        topOrigin: $transaction->getMerchantOrigin(),
        total: PaymentCurrencyAmount::create($transaction->getCurrency(), $transaction->getAmount()),
        instrument: PaymentCredentialInstrument::create(
            $transaction->getInstrumentDisplayName(),
            $transaction->getInstrumentIconUrl(),
        ),
        payeeName: $transaction->getPayeeName(),
        payeeOrigin: $transaction->getPayeeOrigin(),
    );

    // ...build the request options and store the challenge in the session
}
```

`PaymentClientDataCollector` then verifies, field by field, that what the user signed matches what the database said the transaction was — any tampering on the wire results in validation failure.

The transaction record itself carries what makes it safe to confirm only once:

* an ID drawn from a secure random source, such as `bin2hex(random_bytes(16))`, never a sequence number;
* the user it belongs to, checked on every request;
* a short expiry, fifteen minutes for instance;
* a status, set to completed or cancelled as soon as the assertion is verified, so that the same transaction cannot be confirmed twice.

## Browser support

SPC requires Chromium-based browsers (Chrome 105+, Edge 105+, Opera 91+) and an HTTPS context. The user must already have at least one credential registered with `PaymentExtension::register()` enabled.

## Runnable demo

The [webauthn-demos](https://github.com/web-auth/webauthn-demos) repository ships a complete demo under [`spc-demo/`](https://github.com/web-auth/webauthn-demos/tree/main/spc-demo) in three flavours:

* `same-origin/` — single PHP server hosting the relying party and the merchant page.
* `two-origin/` — bank and merchant on separate origins, using CORS.
* `three-tier/` — adds a real merchant backend so the bank ACS hop happens server-to-server, mirroring an EMV 3DS deployment.

Each flavour has a `run.sh` launcher and its own README walking through the EMV 3DS mapping and the trust model.

## See also

* [W3C Secure Payment Confirmation](https://www.w3.org/TR/secure-payment-confirmation/)
* [Extensions](extensions.md) — generic mechanism behind `PaymentExtension`
* [Authentication Without Username](authentication-without-username.md) — usually paired with SPC for one-tap merchant flows
