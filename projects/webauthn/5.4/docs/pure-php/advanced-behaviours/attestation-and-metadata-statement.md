# Attestation and metadata statement

!!! danger

    **Important Notice:** The request for an Attestation Statement is reserved for applications necessitating a high degree of reliability, such as those operated by banking or financial institutions, government agencies, etc. Exercise caution and ensure your application's context requires such a level of trust before proceeding.

## Attestation statement support manager

There are a few steps to achieve. First, you have to add support classes for all attestation statement types into your Attestation Metadata Manager.

!!! warning

    For 4.5.0, the `TPMAttestationStatementSupport` class accepts a PSR-20 clock as argument. This argument will be mandatory for 5.0.0.

    In the example below, we use `symfony/clock` component.

```php linenums="1"
<?php

declare(strict_types=1);

use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\ECDSA;
use Cose\Algorithm\Signature\RSA;
use Webauthn\AttestationStatement\AndroidKeyAttestationStatementSupport;
use Webauthn\AttestationStatement\AttestationStatementSupportManager;
use Webauthn\AttestationStatement\FidoU2FAttestationStatementSupport;
use Webauthn\AttestationStatement\NoneAttestationStatementSupport;
use Webauthn\AttestationStatement\PackedAttestationStatementSupport;
use Webauthn\AttestationStatement\TPMAttestationStatementSupport;
use Webauthn\AttestationStatement\AppleAttestationStatementSupport;
use Symfony\Component\Clock\NativeClock;

//We need a PSR-20 clock
$clock = new NativeClock();

// You normally already do this
$attestationStatementSupportManager = AttestationStatementSupportManager::create();
$attestationStatementSupportManager->add(NoneAttestationStatementSupport::create());

// Additional classes to add
$attestationStatementSupportManager->add(FidoU2FAttestationStatementSupport::create());
$attestationStatementSupportManager->add(AppleAttestationStatementSupport::create());

$attestationStatementSupportManager->add(AndroidKeyAttestationStatementSupport::create());
$attestationStatementSupportManager->add(TPMAttestationStatementSupport::create($clock));

// Cose Algorithm Manager
// The list of algorithm depends on the algorithm list you defined in your options
// You should use at least ES256 and RS256 algorithms that are widely used.
$coseAlgorithmManager = Manager::create();
$coseAlgorithmManager->add(ECDSA\ES256::create());
$coseAlgorithmManager->add(RSA\RS256::create());

$attestationStatementSupportManager->add(PackedAttestationStatementSupport::create($coseAlgorithmManager));

// New in v5.3.0: Compound Attestation Statement Support
use Webauthn\AttestationStatement\CompoundAttestationStatementSupport;
$attestationStatementSupportManager->add(CompoundAttestationStatementSupport::create($attestationStatementSupportManager));
```

!!! warning

    **Changed in v5.3.6:** `AndroidKeyAttestationStatementSupport` verifies the authorization lists of the attestation certificate. The key must have been generated inside the keystore (`origin` equal to `KM_ORIGIN_GENERATED`) and be allowed to sign (`purpose` containing `KM_PURPOSE_SIGN`). The union of the `softwareEnforced` and `teeEnforced` lists is used, as described by the specification. An imported key, accepted by the previous versions, is now rejected.

!!! warning

    **New in v5.3.12:** some TPMs sign their attestation statement with `RS1` (RSASSA-PKCS1-v1\_5 with SHA-1), which is no longer acceptable for digital signatures. Verifying such a statement emits an `E_USER_WARNING`, which becomes fatal wherever an error handler turns warnings into exceptions, and which `web-auth/cose-lib` v5.0.0 will replace with an exception. The algorithm manager is not involved: adding `RS1` to it, even with the acknowledgement, changes nothing for the TPM attestation statement.

If your application has to keep registering these authenticators, for instance to pass the platform attestation tests of the FIDO Conformance Tools, acknowledge the algorithm with the second argument of `TPMAttestationStatementSupport::create()`. Without it, the statement is verified and the warning is emitted, as before.

```php linenums="1"
$attestationStatementSupportManager->add(TPMAttestationStatementSupport::create($clock, true));
```

!!! info

    **Compound Attestation Statement (v5.3.0+):** The Compound Attestation format allows multiple attestation statements to be bundled together. This is useful for authenticators that support multiple attestation mechanisms. The `CompoundAttestationStatementSupport` requires the `AttestationStatementSupportManager` to process the individual attestation statements within the compound format.

!!! warning

    The Android SafetyNet Attestation API is deprecated. Full turndown is planned in June 2024. More information at [https://developer.android.com/training/safetynet/deprecation-timeline](https://developer.android.com/training/safetynet/deprecation-timeline)

    It is not described on this page, but available in the previous versions of the documentation.

## Metadata statement repository

Then, you must prepare a Metadata Statement Repository. This service will manage all Metadata Statements depending on their sources (local storage or distant service).

Your Metadata Statement Repository must implement the interface `Webauthn\MetadataService\MetadataStatementRepository` that has only one method:

* `findOneByAAGUID(string $aaguid)`: this method retrieves the `MetadataStatement` object with AAGUID. It shall return `null` in case of the absence of the MDS.

!!! warning

    The library does not provide any Metadata Statement Repository. It is up to you to select the MDS suitable for your application and store them in your database.

!!! danger

    **Changed in v5.3.13:** a full attestation (basic, AttCA or AnonCA) under the null AAGUID `00000000-0000-0000-0000-000000000000` goes through the same verification as under any other AAGUID: the status reports, the certificate chain and the attestation type are checked ([GHSA-2jv3-c2vg-rhc4](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-2jv3-c2vg-rhc4)). Until then these checks were skipped under the null AAGUID, which the authenticator writes itself: a software authenticator could register a packed, fido-u2f or apple attestation whose certificate it made itself, and have it recorded as basic or anonca.

    FIDO U2F security keys and Apple anonymous attestations report the null AAGUID. When an attestation is requested, they are now refused unless `findOneByAAGUID('00000000-0000-0000-0000-000000000000')` returns a statement whose attestation root certificates include their roots (the Yubico U2F root, the Apple WebAuthn Root CA...). Self attestation, which has no trust path, is not affected.

    Since v5.4.0, they are also accepted, unverified, when the metadata support does not require a statement. See [Authenticators without a metadata statement](#authenticators-without-a-metadata-statement).

## Status report repository

To prevent the use of rogue MDS or deprecated by the manufacturers, Status Reports may be used. The Status Report Repository is a simple service that implements the interface `Webauthn\MetadataService\StatusReportRepository` with a unique method:

* `findStatusReportsByAAGUID(string $aaguid)`: this method returns a list of Status Reports for the given AAGUID.

Every report of the list is read. The registration is refused as soon as one of them is a security notification (`USER_VERIFICATION_BYPASS`, `ATTESTATION_KEY_COMPROMISE`, `USER_KEY_REMOTE_COMPROMISE`, `USER_KEY_PHYSICAL_COMPROMISE`) or `REVOKED`, wherever it sits in the list.

!!! danger

    **Changed in v5.3.13:** until then only the last report of the list was read, and `REVOKED` was not treated as a compromise ([GHSA-p8cj-mmjr-5c2m](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-p8cj-mmjr-5c2m)). The FIDO Metadata Service BLOB does not keep the reports of an entry in chronological order (most entries list the newest first), so a model flagged by a compromise report placed before another report was registered, and a `REVOKED` model always was.

    A model is now refused even when a later report (`UPDATE_AVAILABLE`, a new certification) follows the compromise. Since v5.4.0, a listener can admit such a model, see [Admitting a compromised authenticator](#admitting-a-compromised-authenticator).

## Certificate chain validator

When an attestation statement is received, a certificate chain is constructed. This chain combines certificates from the Metadata Service (MDS), which are trusted, with those provided by the authenticator, which are untrusted.

The Certificate Chain Validator is responsible for this task. The library provides the class `Webauthn\MetadataService\CertificateChain\PhpCertificateChainValidator`  that requires a Symfony Http Client ([for CRL verification](https://en.wikipedia.org/wiki/Certificate_revocation_list)) and a PSR-20 Clock.

```php linenums="1"
<?php

use Webauthn\MetadataService\CertificateChain\PhpCertificateChainValidator;

$certificateChainValidator = PhpCertificateChainValidator::create(
    $httpClient,
    $clock
);
```

!!! danger

    **Changed in v5.3.13:** the `x5c` entries of an attestation statement are always decoded as DER, as the specification requires ([GHSA-c9p6-r72h-rp3x](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-c9p6-r72h-rp3x)). An entry that contained PEM text used to be passed on as it was, and pki-framework and OpenSSL do not read such text the same way: a packed or TPM attestation signed with a software key could be recorded as an attestation of a genuine model, and a `file://` entry could block a PHP worker. The packed, TPM and Android Key supports also verify the signature with the public key of the certificate they have just validated.

    `CertificateToolbox::convertDERToPEM()` and `CertificateToolbox::convertAllDERToPEM()` now always treat their input as DER: PEM input is no longer returned unchanged. Code of your own that passes PEM to them has to pass DER instead.

## Ceremony step manager factory

The services described above must be set to the [Ceremony Step Manager Factory](../input-validation.md). The CSM you will create will verify the attestation statement sent by the authenticator.

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\CeremonyStep\CeremonyStepManagerFactory;

$csmFactory = new CeremonyStepManagerFactory();
$csmFactory->setAttestationStatementSupportManager($attestationStatementSupportManager);
$csmFactory->enableMetadataStatementSupport(
    $metadataStatementRepository,
    $statusReportRepository,
    $certificateChainValidator,
);
$csmFactory->setEventDispatcher($eventDispatcher);
```

The metadata step dispatches the events described below with the PSR-14 dispatcher of the factory. Set it before the factory builds the ceremony step managers (`creationCeremony()`, `conditionalCreateCeremony()`): they keep the dispatcher they were built with. Without a dispatcher, nothing is dispatched and the registrations are verified as described on this page.

## Authenticators without a metadata statement

!!! info

    **New in v5.4.0**

By default, a full attestation (basic, AttCA or AnonCA) whose AAGUID has no Metadata Statement is refused with `The Metadata Statement for the AAGUID "…" is missing`. The FIDO Metadata Service does not list every model, and the specification lets a Relying Party register a credential whose attestation it cannot verify, and treat it as a credential without attestation.

The fourth argument of `enableMetadataStatementSupport()`, `$requireStatement`, is `true` by default. Set it to `false` to accept these attestations:

```php linenums="1"
$csmFactory->enableMetadataStatementSupport(
    $metadataStatementRepository,
    $statusReportRepository,
    $certificateChainValidator,
    false,
);
```

With `false`:

* an AAGUID that has a statement is verified as before: status reports, certificate chain up to the roots of the statement, attestation type;
* an AAGUID that has none, the null AAGUID included, passes without its certificate chain being verified. Its status reports still apply;
* the self attestations and the [enterprise attestations verified up to pinned trust anchors](#trust-anchors-of-the-organization) keep their own handling.

Once a full attestation has passed the metadata checks, the step dispatches `Webauthn\Event\AttestationCheckedAgainstMetadata`. Its `isVerified()` method returns `false` when the model is only declared by the authenticator, that is when `metadataStatement` is `null`. The event also carries the status reports of the AAGUID (`statusReports`) and the credential record the validator returns (`credentialRecord`).

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\Event\AttestationCheckedAgainstMetadata;

$eventDispatcher->addListener(
    AttestationCheckedAgainstMetadata::class,
    static function (AttestationCheckedAgainstMetadata $event) use ($authenticatorModels): void {
        $authenticatorModels->record(
            $event->credentialRecord->publicKeyCredentialId,
            $event->credentialRecord->aaguid->toRfc4122(),
            $event->isVerified()
        );
    }
);
```

`CredentialRecord` has no member for this information: store it next to the credential if your application needs it later.

!!! warning

    The AAGUID is written by the authenticator. When `isVerified()` returns `false`, nothing proves that the authenticator is the model it claims to be: a software authenticator can use any AAGUID the metadata do not know. Do not grant anything on the AAGUID of an unverified attestation.

## Admitting a compromised authenticator

!!! info

    **New in v5.4.0**

A model is refused as soon as one of its status reports is a security notification or `REVOKED` (see [Status report repository](#status-report-repository)). Before refusing it, the step dispatches `Webauthn\Event\CompromisedAuthenticatorDetected`, and the registration goes on only when a listener calls `admit()`. Without a listener or without a dispatcher, the model is refused as before.

The event carries:

* `credentialRecord`: the credential being registered;
* `metadataStatement`: the statement of the AAGUID, or `null` when the AAGUID has none or when the attestation is an enterprise attestation verified up to pinned trust anchors;
* `statusReports`: every status report of the AAGUID;
* `compromisedStatusReports()`: the reports that flag the model as compromised or revoked.

It is dispatched once per registration, whatever the number of reports flagging the model, for full attestations and for self attestations whose AAGUID has a statement.

The example below lets the authenticators of a fleet register until the date they are replaced:

```php linenums="1"
<?php

declare(strict_types=1);

use Webauthn\Event\CompromisedAuthenticatorDetected;

$eventDispatcher->addListener(
    CompromisedAuthenticatorDetected::class,
    static function (CompromisedAuthenticatorDetected $event) use ($clock, $fleetModel, $replacementDeadline): void {
        if ($event->credentialRecord->aaguid->toRfc4122() === $fleetModel && $clock->now() < $replacementDeadline) {
            $event->admit();
        }
    }
);
```

!!! danger

    Admitting a model means accepting the risk the report describes: a bypass of the user verification, a leaked attestation key, keys that can be extracted. Keep the admission as narrow as possible (one model, a deadline) and log it.

## Requesting attestation statement

By default, no Attestation Statement is asked to the Authenticators (type = `none`). To change this behavior, you just have to set the corresponding parameter in the `Webauthn\PublicKeyCredentialCreationOptions` object.

There are 4 conveyance modes available using PHP constants provided by the class `Webauthn\PublicKeyCredentialCreationOptions`:

* `ATTESTATION_CONVEYANCE_PREFERENCE_NONE`: the Relying Party is not interested in authenticator attestation (default)
* `ATTESTATION_CONVEYANCE_PREFERENCE_INDIRECT`: the Relying Party prefers an attestation conveyance yielding verifiable attestation statements, but allows the client to decide how to obtain such attestation statements.
* `ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT`: the Relying Party wants to receive the attestation statement as generated by the authenticator.
* `ATTESTATION_CONVEYANCE_PREFERENCE_ENTERPRISE`: the Relying Party wants an attestation that may identify the authenticator uniquely. See [Enterprise attestation](#enterprise-attestation).

```php linenums="1"
<?php

use Webauthn\PublicKeyCredentialCreationOptions;

$publicKeyCredentialCreationOptions = PublicKeyCredentialCreationOptions::create(
    $relyingParty,
    $userEntity,
    $challenge,
    attestation: PublicKeyCredentialCreationOptions::ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT,
);
```

### attestation on RequestOptions (v5.4.0+)

!!! info

    **New in v5.4.0**

WebAuthn Level 3 §5.5 lets the relying party request an *assertion* attestation through the same `attestation` enum on `PublicKeyCredentialRequestOptions`. The accepted values are identical to creation options (`none`, `indirect`, `direct`, `enterprise`), and the constants are those of `PublicKeyCredentialCreationOptions`:

```php linenums="1"
use Webauthn\PublicKeyCredentialCreationOptions;
use Webauthn\PublicKeyCredentialRequestOptions;

$publicKeyCredentialRequestOptions = PublicKeyCredentialRequestOptions::create(
    challenge: random_bytes(32),
    rpId: 'example.com',
    attestation: PublicKeyCredentialCreationOptions::ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT,
);
```

### attestationFormats (v5.4.0+)

!!! info

    **New in v5.4.0**

WebAuthn L3 §5.4 introduces `attestationFormats`, an ordered list of the formats the relying party prefers. It is exposed on both `PublicKeyCredentialCreationOptions` and `PublicKeyCredentialRequestOptions`:

```php linenums="1"
use Webauthn\PublicKeyCredentialCreationOptions;

$publicKeyCredentialCreationOptions = PublicKeyCredentialCreationOptions::create(
    $relyingParty,
    $userEntity,
    $challenge,
    attestation: PublicKeyCredentialCreationOptions::ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT,
    attestationFormats: ['packed', 'tpm', 'fido-u2f'],
);
```

When the list is non-empty, `CheckAttestationFormatIsKnownAndValid` cross-checks the format the authenticator returned against it and throws `AuthenticatorResponseVerificationException` on mismatch. A list without `none` therefore refuses the anonymized attestations, with `The attestation statement format "none" is not in the list requested by the relying party.` An empty list keeps the historical behaviour (any registered format is accepted). Empty lists are also omitted from the JSON payload, matching the spec's "absent == empty preference" semantics. No Stimulus change is needed: the field rides along inside `optionsJSON` and reaches `navigator.credentials.{create,get}()` as-is.

## Enterprise attestation

!!! info

    **New in v5.4.0**

With the `enterprise` conveyance preference, the Relying Party asks for an attestation that may identify the authenticator uniquely. It is meant for controlled deployments, where an organization wants to tie each registration to a device it manages. The clients only return such an attestation when their configuration (an enterprise policy) or the authenticator (a vendor-facilitated enterprise attestation, provisioned for given RP IDs) permits it for the RP ID. Otherwise they fall back to a regular attestation.

```php linenums="1"
<?php

use Webauthn\PublicKeyCredentialCreationOptions;

$publicKeyCredentialCreationOptions = PublicKeyCredentialCreationOptions::create(
    $relyingParty,
    $userEntity,
    $challenge,
    attestation: PublicKeyCredentialCreationOptions::ATTESTATION_CONVEYANCE_PREFERENCE_ENTERPRISE,
);
```

### Trust anchors of the organization

An enterprise attestation chains to a root certificate of the organization, for instance the identity an organization installs on its managed devices, or to a root certificate the vendor provisions for one customer. No Metadata Statement lists these roots, so such an attestation used to be refused with `The Metadata Statement for the AAGUID "…" is missing`.

Pin the trust anchors of the organization on the factory, as PEM or Base64-encoded DER certificates:

```php linenums="1"
$csmFactory->enableMetadataStatementSupport(
    $metadataStatementRepository,
    $statusReportRepository,
    $certificateChainValidator,
);
$csmFactory->setEnterpriseAttestationTrustAnchors([
    file_get_contents('/path/to/organization-root-ca.pem'),
]);
```

When trust anchors are pinned and the creation options ask for `enterprise`:

* a full attestation (basic, AttCA, AnonCA) is verified with the certificate chain validator up to the pinned anchors only, whether its AAGUID has a Metadata Statement or not, the null AAGUID included. An attestation that chains to none of them is refused;
* the root certificates and the attestation types of the Metadata Statements do not apply;
* the status reports of the AAGUID still apply, and so does the [admission of a compromised authenticator](#admitting-a-compromised-authenticator);
* a certificate chain validator is mandatory: without one, the registration fails with `The Certificate Chain Validator is mandatory when trust anchors are pinned for enterprise attestations.`

Nothing changes for the self and none attestations, for the other conveyance preferences, or when no anchor is pinned. A self or none attestation still passes under `enterprise`: to accept the attested devices of the organization only, check the `attestationType` member of the credential record (`basic`, `attca` or `anonca`). `attestationFormats` can leave `none` out, but a packed attestation may be a self attestation.

### Certificates with the "Enterprise Attestation" unit

The packed format requires the Subject of the attestation certificate to have the Organization Unit `Authenticator Attestation`. Yubico documents the certificates of its enterprise attestations with `OU=Enterprise Attestation`. Since v5.4.0, that unit is also accepted, on a certificate that carries the `id-fido-gen-ce-sernum` extension (`1.3.6.1.4.1.45724.1.1.2`), which the specification reserves for enterprise attestations. The other checks of the certificate and the verification of the signature are unchanged.

### Serial number of the authenticator

An enterprise attestation gives the authenticator a serial number, in the `id-fido-gen-ce-sernum` extension of its packed attestation certificate. `CertificateTrustPath::authenticatorSerialNumber()` reads it from the first certificate of the trust path, and returns `null` when that certificate does not carry the extension.

```php linenums="1"
<?php

use Webauthn\TrustPath\CertificateTrustPath;

$credentialRecord = $authenticatorAttestationResponseValidator->check(
    $authenticatorAttestationResponse,
    $publicKeyCredentialCreationOptions,
    'my-application.com'
);

$trustPath = $credentialRecord->trustPath;
$serialNumber = $trustPath instanceof CertificateTrustPath ? $trustPath->authenticatorSerialNumber() : null;
if ($serialNumber !== null) {
    $deviceId = $credentialRecord->aaguid->toRfc4122().'/'.bin2hex($serialNumber);
}
```

* The value is the raw content of the extension: encode it (`bin2hex()`) before displaying or storing it as text.
* It is unique per authenticator for a given AAGUID only: a device is identified by the pair (AAGUID, serial number).
* It is read from the certificates the trust path already holds, so the credential records stored before 5.4.0 give it too.
* It is returned whatever the creation options asked. Compare `$publicKeyCredentialCreationOptions->attestation` with `enterprise` if you only want it from enterprise attestations.

!!! warning

    **Deprecated in v5.4.0:** the specification requires the extension not to be marked critical and its value to be an OCTET STRING. A packed attestation whose certificate carries a malformed extension is still accepted in 5.4: the extension is ignored, `authenticatorSerialNumber()` returns `null`, and a deprecation is triggered. It is refused in 6.0.0.
