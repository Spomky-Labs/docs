---
description: 'CertificateSignatureVerifier: verifying with the key of an X.509 certificate, beyond what openssl_verify can express.'
---

# Verifying with a certificate

WebAuthn Level 3 §8.2 to §8.4 ask a relying party to verify a packed (`x5c`), TPM or android-key attestation statement
"with the algorithm specified in `alg`", against the key of the attestation certificate. Going through
`Algorithms::getOpensslAlgorithmFor()` and `openssl_verify()` only reaches the algorithms an `OPENSSL_ALGO_*` digest
can describe, ECDSA and RSASSA-PKCS1-v1_5, because that digest implies PKCS #1 v1.5 padding; RSASSA-PSS, EdDSA,
Ed25519 and Ed448 cannot be expressed that way at all. That is the documented scope of `Algorithms::COSE_ALGORITHM_MAP`
and of the accessor that reads it.

`Cose\Algorithm\Signature\CertificateSignatureVerifier` takes the other route: the key of the certificate becomes a
`Cose\Key\Key`, and the `Signature` class registered for the identifier verifies with it.

```php
use Cose\Algorithm\Manager;
use Cose\Algorithm\Signature\CertificateSignatureVerifier;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Algorithm\Signature\ECDSA\ES256K;
use Cose\Algorithm\Signature\FullySpecified\Ed25519;
use Cose\Algorithm\Signature\RSA\PS256;

$manager = Manager::create()->add(ES256::create(), ES256K::create(), PS256::create(), Ed25519::create());
$verifier = CertificateSignatureVerifier::create($manager);

$isValid = $verifier->verify($alg, $certificatePem, $data, $signature);
```

The set of acceptable algorithms is the `Manager` the operator built, not a constant of this library: an `alg` that
comes from the wire cannot select a verifier that was never registered. `RS1` in particular is only reachable when an
`RS1` instance was registered, which can only be built by acknowledging what SHA-1 is.

The verifier configures nothing of its own, so every policy a registered algorithm carries applies unchanged: it is
that very instance which verifies, and the minimum modulus length an RSA algorithm was created with (see
[Validating RSA keys](../keys/validating-rsa-keys.md)) is the one enforced against the key of the certificate.

```php
use Cose\Algorithm\Signature\RSA\RS256;
use Cose\Key\RsaKeyValidator;

// This RS256 refuses a certificate whose modulus is shorter than 3072 bits, through the verifier as anywhere else.
$manager = Manager::create()->add(RS256::create(RsaKeyValidator::create(minimumModulusLength: 3072)));
```

`verify()` returns `false` for every signature the algorithm rejects, and throws an `InvalidArgumentException` when the
certificate cannot be read, when no signature algorithm is registered for the identifier, or when the key of the
certificate cannot be used with that algorithm, the same contract as `Signature::verify()`.

When the certificate travels in the message, `verifyWithX5Chain()` takes the `x5chain` header parameter
([RFC 9360](https://www.rfc-editor.org/rfc/rfc9360.html)) as `CoseHeaders::getX5Chain()` returns it and verifies with
its end-entity certificate; see [X.509 header parameters](../header-parameters/x509.md), and in particular what it says about validating
the rest of the chain.

When the certificate itself is not at hand, `verifySubjectPublicKeyInfo()` takes a SubjectPublicKeyInfo instead, and
`Cose\Key\PublicKeyLoader` exposes the conversion on its own, see
[Loading a key from a certificate](../keys/loading-a-key-from-a-certificate.md).
