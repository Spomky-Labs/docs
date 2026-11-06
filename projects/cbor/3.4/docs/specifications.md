---
description: The specifications, the registry, and the libraries next to this one
---

# Specifications and related libraries

## The format

-   [RFC 8949](https://datatracker.ietf.org/doc/html/rfc8949) — Concise Binary Object Representation
    (CBOR), the current specification. It replaced RFC 7049, which the library's older keywords still
    mention.
-   [IANA CBOR tags registry](https://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml) — which number
    means what, and who registered it.
-   [RFC 8610](https://datatracker.ietf.org/doc/html/rfc8610) — CDDL, a notation for writing down the
    shape a CBOR document must have.

## What is built on it

-   [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052) — COSE, signing and encryption in CBOR. It
    replaced RFC 8152.
-   [RFC 8392](https://datatracker.ietf.org/doc/html/rfc8392) — CWT, CBOR Web Tokens.
-   [RFC 7252](https://datatracker.ietf.org/doc/html/rfc7252) — CoAP, whose payloads are often CBOR.
-   [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428) — SenML, sensor measurements.
-   [WebAuthn](https://www.w3.org/TR/webauthn-3/) — attestation objects and COSE keys.

## Libraries

-   [web-auth/cose-lib](https://github.com/web-auth/cose-lib) — COSE keys, algorithms and verification,
    built on this library.
-   [web-auth/webauthn-framework](https://github.com/web-auth/webauthn-framework) — a WebAuthn server for
    PHP and Symfony.
-   [web-token/jwt-framework](https://github.com/web-token/jwt-framework) — the JSON side of the same
    ideas: JWS, JWE, JWT.
-   [brick/math](https://github.com/brick/math) — the arbitrary-precision arithmetic this library uses for
    big numbers.

Every Spomky-Labs documentation site is listed on [docs.spomky-labs.com](https://docs.spomky-labs.com/).

## This library

-   [The repository](https://github.com/Spomky-Labs/cbor-php)
-   [Issues](https://github.com/Spomky-Labs/cbor-php/issues)
-   [Discussions](https://github.com/Spomky-Labs/cbor-php/discussions)
-   [Packagist](https://packagist.org/packages/spomky-labs/cbor-php)
