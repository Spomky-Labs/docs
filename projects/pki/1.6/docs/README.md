---
description: X.509 certificates, ASN.1 and public key infrastructure for PHP, without a single network call.
---

# PKI Framework

PKI Framework reads, writes and validates the structures a public key infrastructure is made of: X.509
certificates, attribute certificates, certification requests, the ASN.1 types underneath them, and the
textual encodings they travel in. It is a library of data structures and a validator, in pure PHP.

```bash
composer require spomky-labs/pki-framework
```

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;

$certificate = Certificate::fromPEM(PEM::fromFile('server.crt'));

echo $certificate->tbsCertificate()->subject()->toString();   // cn=example.com
echo $certificate->tbsCertificate()->validity()->notAfter()->dateTime()->format('c');
```

## What it covers

| Specification | What the library does with it |
|---|---|
| [X.690](https://www.itu.int/rec/T-REC-X.690) | ASN.1 DER encoding and decoding, every universal type, tagged types, indefinite length |
| [RFC 5280](https://tools.ietf.org/html/rfc5280) | X.509 certificates, their extensions, and certification path validation |
| [RFC 5755](https://tools.ietf.org/html/rfc5755) | Attribute certificates and their validation |
| [RFC 2986](https://tools.ietf.org/html/rfc2986) | PKCS #10 certification requests |
| [RFC 5208](https://tools.ietf.org/html/rfc5208), [RFC 5958](https://tools.ietf.org/html/rfc5958) | PKCS #8 private keys, one asymmetric key |
| [RFC 7468](https://tools.ietf.org/html/rfc7468) | PEM, the textual encoding of all of the above |
| [X.501](https://www.itu.int/rec/T-REC-X.501), [X.520](https://www.itu.int/rec/T-REC-X.520) | Distinguished names, attribute types, name comparison and string preparation |
| [RFC 8410](https://tools.ietf.org/html/rfc8410) | Ed25519, Ed448, X25519 and X448 keys |

## Where to start

- **Reading material you were handed** — [Reading a certificate](certificates/reading-a-certificate.md),
  then [Textual encoding (PEM)](pem/README.md).
- **Checking that a chain leads somewhere you trust** —
  [Validating a path](certification-paths/validating-a-path.md). Read
  [What validation does not do](certification-paths/what-validation-does-not-do.md) before you rely on it.
- **Issuing certificates** — [Issuing a certificate](certificates/issuing-a-certificate.md), and
  [Issuing from a request](certification-requests/issuing-from-a-request.md) when the subject sent a CSR.
- **Working one level down, on the ASN.1 itself** — [ASN.1 and DER](asn1/README.md).

## Two things to know before you build on it

**The library never opens a network connection.** Nothing is fetched from an authority information access
extension, a CRL distribution point or an OCSP responder, and no system trust store is read. Everything
the library trusts, the trust anchors included, is handed to it by your application. Path validation
therefore says nothing about revocation; see
[What validation does not do](certification-paths/what-validation-does-not-do.md).

**Everything a certification request contains was chosen by whoever submitted it.** `TBSCertificate::fromCSR()`
does not verify its signature and never copies the extensions that decide what a certificate may do. Name
the ones you are willing to honour; see [Issuing from a request](certification-requests/issuing-from-a-request.md).

## Credit

The framework started as a fork of the libraries published at [github.com/sop](https://github.com/sop) by
Joni Eskelinen. It has diverged substantially since — the code has been reworked, extended and maintained
to meet the Spomky-Labs requirements — and the two are no longer interchangeable. All credit for the
original work goes to its developer. [Migrating from the sop libraries](migration/from-the-sop-libraries.md)
describes what changed.
