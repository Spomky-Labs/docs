---
description: What changed between the sop libraries and PKI Framework, and what to do in code that used them.
---

# Migrating from the sop libraries

PKI Framework started as a fork of the libraries published at
[github.com/sop](https://github.com/sop) by Joni Eskelinen — `sop/asn1`, `sop/x509`, `sop/x501`,
`sop/crypto-types`, `sop/crypto-encoding`, `sop/crypto-bridge`. It has diverged substantially since, and
**the two are no longer interchangeable**. All credit for the original work goes to its developer.

This page is for code that used the originals.

## One package instead of six

```bash
composer remove sop/asn1 sop/x509 sop/x501 sop/crypto-types sop/crypto-encoding sop/crypto-bridge
composer require spomky-labs/pki-framework
```

Everything is in one package now, autoloaded under one namespace.

## The namespace

| Was | Is |
|---|---|
| `Sop\ASN1\…` | `SpomkyLabs\Pki\ASN1\…` |
| `Sop\X509\…` | `SpomkyLabs\Pki\X509\…` |
| `Sop\X501\…` | `SpomkyLabs\Pki\X501\…` |
| `Sop\CryptoTypes\…` | `SpomkyLabs\Pki\CryptoTypes\…` |
| `Sop\CryptoEncoding\…` | `SpomkyLabs\Pki\CryptoEncoding\…` |
| `Sop\CryptoBridge\…` | `SpomkyLabs\Pki\CryptoBridge\…` |

The class names and the directory layout under each are unchanged, so a search and replace over your
`use` statements covers most of the work:

```bash
grep -rl 'Sop\\' src tests | xargs sed -i \
  -e 's/Sop\\ASN1\\/SpomkyLabs\\Pki\\ASN1\\/g' \
  -e 's/Sop\\X509\\/SpomkyLabs\\Pki\\X509\\/g' \
  -e 's/Sop\\X501\\/SpomkyLabs\\Pki\\X501\\/g' \
  -e 's/Sop\\CryptoTypes\\/SpomkyLabs\\Pki\\CryptoTypes\\/g' \
  -e 's/Sop\\CryptoEncoding\\/SpomkyLabs\\Pki\\CryptoEncoding\\/g' \
  -e 's/Sop\\CryptoBridge\\/SpomkyLabs\\Pki\\CryptoBridge\\/g'
```

Check the diff: a string mentioning `Sop\` in a message or a fixture is not a class reference.

## `new` becomes `create()`

**This is the change that touches the most lines.** Constructors are private or protected, so every class
is built through a static factory and `new` no longer compiles.

```php
// was
$seq = new Sequence(new Integer(1), new UTF8String('x'));
$name = new Name(...$rdns);
$validity = new Validity($notBefore, $notAfter);
$ext = new BasicConstraintsExtension(true, true, 1);

// is
$seq = Sequence::create(Integer::create(1), UTF8String::create('x'));
$name = Name::create(...$rdns);
$validity = Validity::create($notBefore, $notAfter);
$ext = BasicConstraintsExtension::create(true, true, 1);
```

The rule is mechanical: `new X(…)` becomes `X::create(…)`, with the same arguments. The named factories
you already used — `fromPEM()`, `fromDER()`, `fromASN1()`, `fromString()` — are unchanged.

`new OpenSSLCrypto()` still works, since the crypto engine is meant to be extended. Step 2 of the order
below is the cheap way to find the rest: a missed `new` is a hard failure, not a silent one.

## Immutability

Objects do not change. Every `with*()` returns a copy, and the original is untouched:

```php
$tbs->withRandomSerialNumber();              // discarded
$tbs = $tbs->withRandomSerialNumber();       // what you meant
```

That was true of the originals in most places and is now true everywhere, including `Extensions`,
`AttributeCollection` and the ASN.1 structures.

## `DateTimeImmutable`

Dates are `DateTimeImmutable`, never `DateTime`:

```php
$validity->notBefore()->dateTime();          // DateTimeImmutable
PathValidationConfig::create(new DateTimeImmutable(), 3);
```

## Large integers

Serial numbers, RSA moduli and ASN.1 integers come back as **decimal strings**, with
[brick/math](https://github.com/brick/math) underneath:

```php
$tbs->serialNumber();                        // "2569673129085639595562975411803018896"
$integer->number();                          // decimal string
$integer->intNumber();                       // int, throws if it does not fit
$integer->getValue();                        // BigInteger
```

Comparing serial numbers as PHP integers silently stops working above `PHP_INT_MAX`. Compare the
strings, or use `BigInteger`.

## Behaviour that changed, and will break code

These are the ones a search and replace will not find. Each is deliberate.

### Path validation needs a trust anchor

```php
// was: validated against the path's own first certificate, silently
$path->validate($config);

// is
$path->validate($config->withTrustAnchor($root));
// or, better, build the path from your trust list
$path = CertificationPath::toTarget($target, $trustAnchors, $intermediates);
$path->validate($config);
```

A path from `fromCertificateChain()` now **throws** without an anchor. A path from `create()` raises a
deprecation notice and still falls back, so you can find your call sites before the fallback goes. See
[Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input).

### `fromCSR()` no longer copies every requested extension

```php
// was: every requested extension was copied
$tbs = TBSCertificate::fromCSR($csr);

// is: name what you honour
$tbs = TBSCertificate::fromCSR($csr, [Extension::OID_SUBJECT_ALT_NAME]);
```

The extensions that decide what a certificate may do are never copied, whatever you pass. Leaving the
argument out raises a deprecation notice and will become an empty allow list. See
[Issuing from a request](../certification-requests/issuing-from-a-request.md).

### `Certificate::equals()` is now an exact comparison

It compares the two encodings octet by octet. It used to compare the serial number, the subject key
identifier and the subject DN — three public values anyone can repeat — so it reported two certificates
as the same when they differed in issuer, validity, every extension and the signature.

`CertificateBundle::contains()` is built on it and became exact with it. If you relied on the looser
grouping, `hasEqualSubjectIdentity()` is it — and read
[what it does not tell you](../names/comparing-names.md#comparing-certificates-not-names).

### Signature algorithms and key sizes are filtered

Path validation refuses an algorithm outside `allowedSignatureAlgorithms()` and an RSA modulus below
`minimumRSAKeySize()`. MD2, MD4 and MD5 are refused by default; the defaults still accept SHA-1 and 1024
bits. A chain that used to validate may now be refused — which is the point. See
[Configuration](../certification-paths/configuration.md).

### RSASSA-PSS certificates are refused when parsed

Not implemented, and deliberately absent from the allowed set rather than advertised and broken.

### Decoding is bounded and its exceptions are normalised

Nesting is capped at 64 levels, and nothing but `DecodeException` escapes `Element::fromDER()` — the
original type is kept as its previous. A `catch` for something narrower may stop matching. See
[Decoding untrusted input](../asn1/untrusted-input.md).

### Serial numbers are random by default

`sign()` draws a 20-octet serial number when none was set, rather than writing a zero. A fixed serial
number below nine octets raises a deprecation notice.

### Repeated optional fields are refused

A structure carrying the same context-specific tag twice raises `DecodeException` rather than being read
as its last copy.

### Name comparison prepares each side under its own syntax

The same name written as a `BMPString` and as a `PrintableString` now compares equal, where it used to be
two different names — which meant a `directoryName` a constraint excluded was reachable by re-encoding
it. See [Comparing names](../names/comparing-names.md).

## PHP version

PHP 8.1 or later, and `mbstring` is required. See
[Prerequisites](../introduction/pre-requisite.md).

## A migration order that works

1. Replace the packages, run the namespace replacement, and let the autoloader find what is left.
2. Replace `new X(…)` with `X::create(…)`, guided by the errors. Private constructors make every missed
   one a hard failure rather than a silent one.
3. Run your test suite with `E_USER_DEPRECATED` visible. The two notices that matter — the path
   validation fallback and the `fromCSR()` deny list — are both security decisions, and both are going
   away.
4. Fix the `with*()` return values you were discarding.
5. Re-read [Security recommendations](../introduction/security-recommendations.md). Several defaults are
   stricter than the originals', and a few are still looser than a new deployment should accept.
