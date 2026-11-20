# Secure payment confirmation (SPC)

!!! info

    **New in v5.4.0**

[Secure Payment Confirmation](https://www.w3.org/TR/secure-payment-confirmation/) is a W3C Web API that lets the relying party authenticate a payment with WebAuthn while having the user agent display the transaction details (amount, payee, instrument) in its own trusted UI. It is the building block recommended by EMV 3DS v2.3.1.1 §6.1.4.1.5 for FIDO-based SCA.

The framework ships SPC support out of the box: a `payment` extension, a dedicated client-data collector, the verification of the browser-bound signature, and a Stimulus controller.

## How the pieces fit together

W3C SPC splits the verification work in two, and the framework wires both:

1. **`clientDataJSON.payment`** carries the transaction the user actually confirmed in the browser SPC dialog. It is signed by the authenticator and validated server-side by `PaymentClientDataCollector`, which compares each field (`rpId`, `topOrigin`, `total`, `instrument`, `payee*`) with the request options. This closes the threat of a compromised client substituting the amount the user signs.
2. **The browser-bound key** binds the payment to the device. The user agent puts its public key, a base64url COSE key, in `clientDataJSON.payment.browserBoundPublicKey`, and the signature it makes with the private key over the raw `clientDataJSON` in `clientExtensionResults.payment.browserBoundSignature.signature`, at registration and at authentication. `CheckBrowserBoundSignature` verifies them in every ceremony built by `CeremonyStepManagerFactory` whose options carry the `payment` extension. See [Browser-bound key](#browser-bound-key).

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

The Symfony bundle auto-registers `PaymentClientDataCollector` and `PaymentExtensionOutputChecker`, and the ceremony always verifies the browser-bound signature, so a regular `AuthenticatorAssertionResponseValidator::check(...)` call performs full SPC validation:

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

The browser-bound signature is a client extension result: the client must send `clientExtensionResults` with the credential, as the Stimulus controllers do. Deserialize the whole credential with the serializer of the library, which attaches these results to `$publicKeyCredential->response`.

For pure PHP usage, wire the new pieces into the ceremony manager factory yourself. `PaymentExtensionOutputChecker` is optional: it only rejects a `payment` entry in the authenticator data, where a conforming authenticator never puts one.

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

## Browser-bound key

The user agent creates the browser-bound key when the credential is registered with `PaymentExtension::register()`, and returns its outputs at registration and at each payment. It may also return none: when it supports none of the algorithms of `browserBoundPubKeyCredParams`, or when it cannot store the key. `CheckBrowserBoundSignature` therefore applies these rules:

| Outputs returned | Outcome |
| --- | --- |
| Neither the public key nor the signature | Accepted: the ceremony relies on the passkey signature alone, as the specification allows |
| Both | The signature must verify over the raw `clientDataJSON` with the public key, otherwise the ceremony fails |
| Only one of them, or a malformed value | The ceremony fails. At authentication, the public key is part of the client data signed by the authenticator, so a missing signature means that the client dropped it, typically by not sending `clientExtensionResults` |

After a successful ceremony, a public key found in the client data has proven possession of its private key. To bind payments to a device, store it at registration and compare it on the next authentications.

Denormalize the client data of the response into `CollectedClientPaymentData` with the serializer of the library (see [Input loading](../input-loading.md); with the Symfony bundle, inject `Symfony\Component\Serializer\Normalizer\DenormalizerInterface`). Its `payment` member is a `CollectedClientAdditionalPaymentRegistrationData` at registration and a `CollectedClientAdditionalPaymentData` at authentication. Both give the key as a `BrowserBoundPublicKey`, or `null` when the user agent returned none:

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\SecurePaymentConfirmation\CollectedClientPaymentData;

$clientData = $publicKeyCredential->response->clientDataJSON;
$browserBoundPublicKey = null;
if ($clientData->has('payment')) {
    $paymentData = $serializer->denormalize($clientData->data, CollectedClientPaymentData::class);
    $browserBoundPublicKey = $paymentData->payment->browserBoundPublicKey;
}

if ($browserBoundPublicKey !== null) {
    $coseKey = $browserBoundPublicKey->publicKey;
    $algorithm = $browserBoundPublicKey->algorithm();
}
```

`publicKey` holds the decoded COSE_Key bytes. They are the same at registration and at authentication, so comparing them is enough to recognize the key. `algorithm()` returns the `alg` member of the COSE_Key, for instance `-7` for ES256, and `coseKey()` the decoded `Cose\Key\Key`. Both refuse with an `InvalidDataException` a key that is not a COSE_Key with an integer `alg` member. That cannot happen after a successful ceremony: `CheckBrowserBoundSignature` decodes the key the same way to verify the signature.

The specification leaves this comparison to the relying party: the library verifies each signature, it does not keep the key.

## Data structures

All value objects live under the `Webauthn\SecurePaymentConfirmation` namespace and validate their inputs in the constructor (ISO 4217 currencies, W3C decimal monetary regex, URL validation on origins, non-empty strings on names).

| Class | Purpose |
| --- | --- |
| `PaymentCurrencyAmount` | ISO 4217 currency + decimal value (`'EUR'`, `'99.99'`). |
| `PaymentCredentialInstrument` | `displayName`, `icon` (a URL), `iconMustBeShown` (`true` by default) and optional `details`. |
| `CollectedClientAdditionalPaymentData` | Mirrors what the browser signs in `clientDataJSON.payment` at authentication, checked by `PaymentClientDataCollector`. |
| `CollectedClientAdditionalPaymentRegistrationData` | `clientDataJSON.payment` at registration: the browser-bound public key only. |
| `CollectedClientPaymentData` | The client data of an SPC ceremony. Its `payment` member is the registration dictionary when the client data type is `webauthn.create`, and the authentication one otherwise. |
| `PaymentEntityLogo` | Optional `paymentEntitiesLogos[]` entry. |
| `BrowserBoundPublicKey` | The browser-bound public key: the decoded COSE_Key bytes, with `algorithm()` for its `alg` member and `coseKey()` for the decoded key. The serializer reads and writes it as the base64url string of the client data. |
| `BrowserBoundSignature` | The browser-bound signature bytes. |
| `BrowserBoundSignatureVerifier` | Decodes the COSE key with `BrowserBoundPublicKey::coseKey()`, looks up the `Cose\Algorithm\Signature\Signature` matching `algorithm()` and verifies the signature against raw `clientDataJSON`. ECDSA signatures are accepted in DER form, as the platform key stores produce them, or in the raw COSE form. |

## Stimulus controller

The Stimulus package ships a `PaymentController` that extends `AuthenticationController`. It forwards the server-issued `payment` extension input to the user agent untouched. On the way back, the controllers base64url-encode `browserBoundSignature.signature` and send it with the credential, at authentication and, through the registration controller, at registration. The deprecated `webauthn` controller does the same.

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
