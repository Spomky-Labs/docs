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

## Status report repository

To prevent the use of rogue MDS or deprecated by the manufacturers, Status Reports may be used. The Status Report Repository is a simple service that implements the interface `Webauthn\MetadataService\StatusReportRepository` with a unique method:

* `findStatusReportsByAAGUID(string $aaguid)`: this method returns a list of Status Reports for the given AAGUID.

Every report of the list is read. The registration is refused as soon as one of them is a security notification (`USER_VERIFICATION_BYPASS`, `ATTESTATION_KEY_COMPROMISE`, `USER_KEY_REMOTE_COMPROMISE`, `USER_KEY_PHYSICAL_COMPROMISE`) or `REVOKED`, wherever it sits in the list.

!!! danger

    **Changed in v5.3.13:** until then only the last report of the list was read, and `REVOKED` was not treated as a compromise ([GHSA-p8cj-mmjr-5c2m](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-p8cj-mmjr-5c2m)). The FIDO Metadata Service BLOB does not keep the reports of an entry in chronological order (most entries list the newest first), so a model flagged by a compromise report placed before another report was registered, and a `REVOKED` model always was.

    A model is now refused even when a later report (`UPDATE_AVAILABLE`, a new certification) follows the compromise. To admit such a model, leave that report out of what your `StatusReportRepository` returns.

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
```

## Requesting attestation statement

By default, no Attestation Statement is asked to the Authenticators (type = `none`). To change this behavior, you just have to set the corresponding parameter in the `Webauthn\PublicKeyCredentialCreationOptions` object.

There are 3 conveyance modes available using PHP constants provided by the class `Webauthn\PublicKeyCredentialCreationOptions`:

* `ATTESTATION_CONVEYANCE_PREFERENCE_NONE`: the Relying Party is not interested in authenticator attestation (default)
* `ATTESTATION_CONVEYANCE_PREFERENCE_INDIRECT`: the Relying Party prefers an attestation conveyance yielding verifiable attestation statements, but allows the client to decide how to obtain such attestation statements.
* `ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT`: the Relying Party wants to receive the attestation statement as generated by the authenticator.

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

WebAuthn Level 3 §5.5 lets the relying party request an *assertion* attestation through the same `attestation` enum on `PublicKeyCredentialRequestOptions`. The accepted values are identical to creation options (`none`, `indirect`, `direct`, `enterprise`):

```php linenums="1"
use Webauthn\PublicKeyCredentialRequestOptions;

$publicKeyCredentialRequestOptions = PublicKeyCredentialRequestOptions::create(
    challenge: random_bytes(32),
    rpId: 'example.com',
    attestation: PublicKeyCredentialRequestOptions::ATTESTATION_CONVEYANCE_PREFERENCE_DIRECT,
);
```

### attestationFormats (v5.4.0+)

!!! info

    **New in v5.4.0**

WebAuthn L3 §5.4 introduces `attestationFormats` — an ordered list of the formats the relying party prefers. It is exposed on both `PublicKeyCredentialCreationOptions` and `PublicKeyCredentialRequestOptions`:

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

When the list is non-empty, `CheckAttestationFormatIsKnownAndValid` cross-checks the format the authenticator returned against it and throws `AuthenticatorResponseVerificationException` on mismatch. An empty list keeps the historical behaviour (any registered format is accepted). Empty lists are also omitted from the JSON payload, matching the spec's "absent == empty preference" semantics — no Stimulus change is needed: the field rides along inside `optionsJSON` and reaches `navigator.credentials.{create,get}()` as-is.
