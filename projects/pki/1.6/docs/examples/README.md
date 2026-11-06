---
description: Complete, runnable examples built out of the pieces the rest of this documentation describes.
---

# Examples

Three worked examples, each one complete enough to run. They assume `composer require
spomky-labs/pki-framework`, `ext-openssl` and either `gmp` or `bcmath`; see
[Prerequisites](../introduction/pre-requisite.md).

- **[A self-signed certificate](a-self-signed-certificate.md)** — the shortest thing worth doing: a key,
  a name, a certificate, and reading it back.
- **[A small certificate authority](a-small-certificate-authority.md)** — a root, an intermediate, an
  end-entity certificate issued from a request, and the path that validates it.
- **[Verifying a TLS chain](verifying-a-tls-chain.md)** — the one most applications actually need: a
  chain a peer sent, a trust store you control, and the checks validation leaves to you.

## Before you copy any of them

Every example omits error handling that production code needs, and says so where it matters. Two things
no example can decide for you:

- **the trust anchor is yours to name** — see
  [Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input);
- **a successful validation is not a complete check** — see
  [What validation does not do](../certification-paths/what-validation-does-not-do.md).

The [security recommendations](../introduction/security-recommendations.md) are the short version of both.

## Generating the keys

The library does not generate keys. Each example starts from a PEM file written by OpenSSL:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out key.pem
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out ec.pem
openssl genpkey -algorithm ED25519 -out ed.pem
```

All three write a `PRIVATE KEY` block, which `PrivateKeyInfo::fromPEM()` reads directly.
