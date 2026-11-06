# Input validation

The loaded data needs to be verified. The library will perform several actions to make sure the input you received is valid. This verification process is performed by a Ceremony Step Manager (CSM). The WebAuthn specification distinguishes two types of ceremonies [described in this page](../webauthn-in-a-nutshell/ceremonies.md).

!!! info

    **Changed in v5.3.11:** the `tokenBinding` member of the client data is validated again when the client sends it. The member is reserved since WebAuthn Level 3, which still defines the dictionary it holds ([section 5.8.1](https://www.w3.org/TR/webauthn-3/#dictionary-client-data)). The value must be an object whose `status` is `present` or `supported`, the two values of the specification, or `not-supported`, which the FIDO Conformance Tools accept as well. When the status is `present`, the object must also carry a non-empty `id`. Any other value fails the ceremony with an `InvalidDataException`.

    Client data without the member, or with a `null` one, is accepted. The value itself is never used and stays available through the `data` property of `CollectedClientData`. From v5.3.6 to v5.3.10, the member was not validated at all.

## Ceremony step manager factory

To facilitate the creation of the CSM, a default factory is included. This factory requires no external services to function.

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\CeremonyStep\CeremonyStepManagerFactory;

$csmFactory = new CeremonyStepManagerFactory();

$creationCSM = $csmFactory->creationCeremony();
$requestCSM = $csmFactory->requestCeremony();
```

!!! info

    You can customize its behavior to fit the specific needs of your application by modifying the provided factory. Please refer to the dedicated pages for more information.

    * [Counter Checker](advanced-behaviours/authenticator-counter.md)
    * [Attestation Statement Support Manager](advanced-behaviours/attestation-and-metadata-statement.md#attestation-statement-support-manager)
    * [Extension Output Checker Handler](advanced-behaviours/extensions.md)
    * [Algorithm Manager](advanced-behaviours/authenticator-algorithms.md)
    * [Metadata Statement Repository](advanced-behaviours/attestation-and-metadata-statement.md#metadata-statement-repository)
    * [Status Report Repository](advanced-behaviours/attestation-and-metadata-statement.md#status-report-repository)
    * [Certification Chain Validator](advanced-behaviours/attestation-and-metadata-statement.md#certificate-chain-validator)

These CSM services are meant to be used by Response Validators. In a similar way, there are two types of validators:

* **Authenticator Attestation Response Validator**: used during the creation ceremony
* **Authenticator Assertion Response Validator**: used during the request ceremony

## Response validators

The Authenticator Attestation Response Validator and Authenticator Assertion Response Validator services are directly used when receiving Authenticator Responses in order to [register authenticators](authenticator-registration.md) or [authenticate users](authenticate-your-users.md).

!!! info

    All null values below correspond to deprecated parameters. They have been removed in 5.0.0

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\AuthenticatorAttestationResponseValidator;
use Webauthn\AuthenticatorAssertionResponseValidator;

$authenticatorAttestationResponseValidator = AuthenticatorAttestationResponseValidator::create(
    $creationCSM
);
$authenticatorAssertionResponseValidator = AuthenticatorAssertionResponseValidator::create(
    $requestCSM
);
```
