---
description: The PHP version and the extensions PKI Framework needs, and the ones that change what it can do.
---

# Prerequisites

## PHP and required extensions

- **PHP 8.1** or later.
- **`mbstring`**, required. The X.520 string preparation steps that make name comparison work transcode
  and normalise text with it.

## Arithmetic: `gmp` or `bcmath`

Serial numbers, RSA moduli and large integers do not fit in a PHP integer, so they go through
[brick/math](https://github.com/brick/math), which is installed with the library. It uses `gmp` if it is
loaded, `bcmath` if it is not, and falls back to a pure-PHP implementation otherwise.

**Install `gmp`, or `bcmath`.** The fallback is correct but slow enough to matter as soon as you parse
certificates in a loop or validate a path.

## `openssl`: needed to sign and to verify

Signing and verifying go through a crypto engine, and the only one shipped is
[`OpenSSLCrypto`](../keys/the-crypto-engine.md). Without `ext-openssl`, `Crypto::getDefault()` throws, and
with it every call that signs or verifies:

- `TBSCertificate::sign()`, `CertificationRequestInfo::sign()`, `AttributeCertificateInfo::sign()`;
- `Certificate::verify()`, `CertificationRequest::verify()`, `AttributeCertificate::verify()`;
- `CertificationPath::validate()` and `ACValidator::validate()`.

Reading, writing and inspecting structures need none of it. A service that only parses certificates it is
handed runs without `openssl`.

## `sodium`: Ed25519 where OpenSSL has no EdDSA

Ed25519 and Ed448 are in the default set of allowed signature algorithms, but whether a signature made
with them can actually be checked depends on the runtime. The OpenSSL extension only grew EdDSA
recently; `ext-sodium`, bundled since PHP 7.2, covers Ed25519 alone.

Verification fails closed where the runtime cannot do it, which surfaces as a path that does not
validate. Ask before you configure rather than after:

```php
use SpomkyLabs\Pki\CryptoBridge\Crypto\OpenSSLCrypto;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Asymmetric\Ed25519AlgorithmIdentifier;

$crypto = new OpenSSLCrypto();

if (! $crypto->supportsSignatureAlgorithm(Ed25519AlgorithmIdentifier::create())) {
    // narrow the configured set rather than have a chain refused during validation
}
```

See [Configuration](../certification-paths/configuration.md#allowed-signature-algorithms).

## Summary

| Extension | Status | Without it |
|---|---|---|
| `mbstring` | Required | The library does not install |
| `gmp` or `bcmath` | Strongly recommended | Correct, but slow on large integers |
| `openssl` | Needed to sign or verify | Parsing works; signing, verifying and path validation throw |
| `sodium` | Optional | Ed25519 cannot be verified on a runtime whose OpenSSL has no EdDSA |
