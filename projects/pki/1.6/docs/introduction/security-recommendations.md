---
description: The decisions PKI Framework leaves to you, and the defaults that are looser than you may expect.
---

# Security recommendations

The library parses, builds and validates structures. It does not decide what you trust. This page lists
every decision it hands back to you, and every default that is looser than a new deployment would
choose.

Read it before you ship. Each item links to the page that explains it in full.

## Name the trust anchor

!!! danger "A path validated without an anchor proves nothing"

    Left to itself, validation falls back to the first certificate of the path — one the peer chose — and
    confirms only that the chain is internally consistent.

Build the path from the certificates you trust and let the library find its way to the target:

```php
$path = CertificationPath::toTarget($leafFromPeer, $trustAnchors, $intermediatesFromPeer);
$result = $path->validate(PathValidationConfig::defaultConfig());
```

A path built by `fromCertificateChain()` refuses to validate without an explicit anchor. One built by
`create()` raises a deprecation notice when it falls back, so you can find the call sites before the
fallback is removed in the next major release. See
[Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input).

## Treat a certification request as untrusted input

!!! warning "`fromCSR()` does not verify the signature, and the default extension policy is a deny list"

Call `CertificationRequest::verify()` yourself, then name the extensions you are willing to honour:

```php
$tbsCertificate = TBSCertificate::fromCSR($csr, [Extension::OID_SUBJECT_ALT_NAME]);
```

Leaving the second argument out copies every requested extension that is not forbidden and raises a
deprecation notice. That default is a deny list, so every extension invented in the future would be
copied by it. See [Issuing from a request](../certification-requests/issuing-from-a-request.md).

## Check revocation yourself

Path validation says the chain is well-formed and leads to an anchor you named. It does **not** say the
certificate is still valid. The library has no CRL parser and no OCSP client, and never opens a
connection, so **a revoked certificate validates**. See
[What validation does not do](../certification-paths/what-validation-does-not-do.md).

## Narrow the signature algorithms and the RSA floor

The defaults carry what deployed PKIs still use, not what a new one should accept.

| Setting | Default | Hardened |
|---|---|---|
| Signature algorithms | `DEFAULT_ALLOWED_SIGNATURE_ALGORITHMS`, which **includes SHA-1** | `HARDENED_ALLOWED_SIGNATURE_ALGORITHMS` |
| RSA modulus | `DEFAULT_MINIMUM_RSA_KEY_SIZE`, **1024 bits** | `HARDENED_MINIMUM_RSA_KEY_SIZE`, 2048 bits |

```php
$config = PathValidationConfig::defaultConfig()
    ->withAllowedSignatureAlgorithms(...PathValidationConfig::HARDENED_ALLOWED_SIGNATURE_ALGORITHMS)
    ->withMinimumRSAKeySize(PathValidationConfig::HARDENED_MINIMUM_RSA_KEY_SIZE);
```

Chosen-prefix collisions against SHA-1 have been practical since 2020, and the CA/Browser Forum has
required 2048-bit RSA since 2014. The defaults are what they are because raising them in a patch release
would silently cut off legacy enterprise and device PKIs. If yours is not one of them, harden it. These
are the values the defaults will become in a future major release. See
[Configuration](../certification-paths/configuration.md).

## Know whether your runtime can verify EdDSA

Ed25519 and Ed448 are allowed by default, but verification depends on the extensions loaded: the OpenSSL
extension only grew EdDSA recently, and `ext-sodium` covers Ed25519 alone. Verification **fails closed**,
which surfaces as a chain that will not validate. Ask up front with
`OpenSSLCrypto::supportsSignatureAlgorithm()` rather than debugging it later. See
[Prerequisites](pre-requisite.md#sodium-ed25519-where-openssl-has-no-eddsa).

## Name the attribute authorities you trust

Attribute certificate validation does not implement RFC 5755 section 5 check 4 on its own. Without
`ACValidationConfig::withTrustedAttributeAuthorities()`, the validator accepts whatever end-entity
certificate the issuer path ends in. See
[Validating an attribute certificate](../attribute-certificates/validating-an-attribute-certificate.md).

## Compare certificates with the right question

- `Certificate::equals()` compares the two encodings octet by octet. `CertificateBundle::contains()` is
  built on it.
- `Certificate::hasEqualSubjectIdentity()` asks the looser question: same subject, same key, same serial
  number. **It is not an identity check** — two certificates can agree on all three and still be issued
  by different issuers with different extensions.

## Bound what you decode

DER decoding recurses, so nesting is capped at `Element::DEFAULT_MAX_NESTING_DEPTH`, 64 levels. A real
X.509 structure rarely nests deeper than ten. If you decode material from the open internet, lower it:

```php
Element::setMaxNestingDepth(16);
```

The cap is global process state, not per call. Size is yours to bound: the library decodes the string you
give it, so cap the length of an upload before you hand it over. See
[Decoding untrusted input](../asn1/untrusted-input.md).

## Give certificates a random serial number

A constant serial number removes the unpredictability that protects issuance against collision attacks,
and breaks CRL revocation, which identifies a certificate by the (issuer, serial number) pair.
`sign()` draws one when none was set. If you set one yourself, draw at least nine octets —
`MIN_RANDOM_SERIAL_SIZE` — which is the 64 bits of CSPRNG output the CA/Browser Forum Baseline
Requirements ask for, plus the octet the sign bit costs:

```php
$tbsCertificate = $tbsCertificate->withRandomSerialNumber(); // 20 octets, the RFC 5280 maximum
```

See [Issuing a certificate](../certificates/issuing-a-certificate.md#the-serial-number).

## Leave version 1 and version 2 intermediates alone

RFC 5280 section 6.1.4 (k) lets a version 1 or version 2 certificate act as a CA only once the
application has confirmed out of band that it is one. `withLegacyV1IntermediatesTrusted(true)` is how you
state that you did. Do not set it to work around a chain you do not understand.

## Declare the critical extensions you handle

A critical extension the validator does not recognise makes validation fail, as it should. If your
application processes one by its own means, say so with `withAdditionalCriticalExtensions()`. Naming an
extension there means *you* check it — the validator then only stops objecting.

## Hostname matching is yours

The library gives you the subject DN and the subject alternative names. It does not check that a
certificate is the right one for `example.com`, and path validation never looks at a hostname. That
comparison, with the rules of the protocol you are speaking, is a step of your own.
