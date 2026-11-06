---
description: What PKI Framework implements, and what it deliberately leaves to the calling application.
---

# Provided features

PKI Framework is a set of data structures and one validator. Each namespace of the library maps to a
specification, and the pages of this documentation follow the same split.

## The layers

| Namespace | What lives there |
|---|---|
| `SpomkyLabs\Pki\ASN1` | ASN.1 types and the DER codec: [ASN.1 and DER](../asn1/README.md) |
| `SpomkyLabs\Pki\CryptoEncoding` | PEM, a single block or a bundle: [Textual encoding (PEM)](../pem/README.md) |
| `SpomkyLabs\Pki\CryptoTypes` | Keys, algorithm identifiers, signatures: [Keys, algorithms and signatures](../keys/README.md) |
| `SpomkyLabs\Pki\CryptoBridge` | The engine that signs and verifies: [The crypto engine](../keys/the-crypto-engine.md) |
| `SpomkyLabs\Pki\X501` | Distinguished names, attributes, comparison: [Names and attributes](../names/README.md) |
| `SpomkyLabs\Pki\X509` | Certificates, requests, attribute certificates, paths |

## What is implemented

**ASN.1, after X.690.** Every universal type, primitive and constructed, with DER encoding and decoding.
Implicit and explicit tagging, application and private classes, indefinite length, constructed strings.
A decoded element is handed back through [`UnspecifiedType`](../asn1/README.md#unspecifiedtype), which
makes you say what you expected.

**X.509 certificates, after RFC 5280.** Reading, building and signing, with twenty-odd extensions parsed
into their own classes: basic constraints, key usage, extended key usage, subject and issuer alternative
names, name constraints, policy constraints, policy mappings, inhibit anyPolicy, certificate policies,
authority and subject key identifiers, CRL distribution points, freshest CRL, authority and subject
information access, subject directory attributes, target information, AA controls, and no revocation
available. An extension the library does not know becomes an `UnknownExtension` rather than an error.

**Certification path building and validation, after RFC 5280 section 6.** All paths or the shortest path
from a trust list to a target, then the full validation algorithm: signatures, validity periods, basic
constraints and path length, key usage, name constraints, and the policy tree with mapping, explicit
policy and anyPolicy inhibition.

**Certification requests, after RFC 2986.** PKCS #10: reading, building, signing, verifying, and the
extension request attribute. Turning one into a certificate is the issuer's job and is
[deliberately narrow](../certification-requests/issuing-from-a-request.md).

**Attribute certificates, after RFC 5755.** Holder, issuer, validity period, the IETF attribute syntax
and the role, group, access identity, charging identity and authentication info attributes. Validation of
the holder and issuer paths, the targets, and the attribute authority.

**Keys, after PKCS and RFC 8410.** RSA, EC, RSASSA-PSS, Ed25519, Ed448, X25519 and X448, as PKCS #8
`OneAsymmetricKey` / `PrivateKeyInfo`, as `SubjectPublicKeyInfo`, and in their own legacy formats.

**Names, after X.501 and X.520.** Distinguished names from and to the RFC 4514 string form, the standard
attribute types, and name comparison with the matching rules and string preparation the specifications
ask for.

## What is not implemented

These are design decisions, not gaps waiting for a patch.

**No network.** The library never opens a connection. Nothing is fetched from an authority information
access extension, a CRL distribution point or an OCSP responder.

**No revocation checking.** There is no CRL parser and no OCSP client. A revoked certificate validates:
see [What validation does not do](../certification-paths/what-validation-does-not-do.md).

**No system trust store.** Trust anchors are an input to validation, never a discovery.

**No RSASSA-PSS signatures.** A PSS-signed certificate is refused when it is parsed. The OID is
deliberately absent from the default set of allowed signature algorithms, since allowing it would
advertise a capability that does not exist.

**No hostname matching.** Checking that a certificate is the right one for `example.com` is a step of its
own, which the library does not perform. It gives you the subject DN and the subject alternative names;
the comparison, and the rules of the protocol you are speaking, are yours.

**No key generation.** Generate keys with `ext-openssl`, `ext-sodium` or anything else, then read them in
with [`PrivateKeyInfo::fromPEM()`](../keys/private-keys.md).
