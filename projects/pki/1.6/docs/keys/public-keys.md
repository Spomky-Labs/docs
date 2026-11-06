---
description: Getting a public key out of a certificate or a file, and reading the key material inside.
---

# Public keys

`PublicKeyInfo` is the `SubjectPublicKeyInfo` of RFC 5280: an algorithm identifier and a bit string. It
is what a certificate carries and what every `verify()` in the library takes.

## Where one comes from

=== "A certificate"

    ```php
    $publicKeyInfo = $certificate->tbsCertificate()->subjectPublicKeyInfo();
    ```

=== "A certification request"

    ```php
    $publicKeyInfo = $csr->certificationRequestInfo()->subjectPKInfo();
    ```

=== "A private key"

    ```php
    $publicKeyInfo = $privateKeyInfo->publicKeyInfo();
    ```

=== "A file"

    ```php
    use SpomkyLabs\Pki\CryptoEncoding\PEM;
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PublicKeyInfo;

    $publicKeyInfo = PublicKeyInfo::fromPEM(PEM::fromFile('pub.pem'));
    $publicKeyInfo = PublicKeyInfo::fromDER($der);
    ```

=== "A validated path"

    ```php
    $publicKeyInfo = $path->validate($config)->getPublicKeyInfo();
    ```

    The public key of the end-entity certificate, as validation worked it out. See
    [Validating a path](../certification-paths/validating-a-path.md#the-result).

## What it gives you

```php
$publicKeyInfo->algorithmIdentifier();   // RSA, EC, Ed25519, …
$publicKeyInfo->publicKeyData();         // the BitString, as encoded
$publicKeyInfo->publicKey();             // the decoded key
$publicKeyInfo->keyIdentifier();         // 20 bytes, RFC 5280 method 1
$publicKeyInfo->keyIdentifier64();       // 8 bytes, method 2
$publicKeyInfo->toPEM()->string();
```

## The key inside

=== "RSA"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\RSA\RSAPublicKey;

    /** @var RSAPublicKey $key */
    $key = $publicKeyInfo->publicKey();

    $key->modulus();          // decimal string
    $key->publicExponent();
    ```

    The modulus is a decimal string, so its size in bits is a question for
    [brick/math](https://github.com/brick/math) rather than `strlen()`:

    ```php
    use Brick\Math\BigInteger;

    $bits = BigInteger::of($key->modulus())->getBitLength();
    ```

    Path validation already refuses a modulus below
    [`minimumRSAKeySize()`](../certification-paths/configuration.md#the-rsa-floor).

=== "Elliptic curve"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\EC\ECPublicKey;

    /** @var ECPublicKey $key */
    $key = $publicKeyInfo->publicKey();

    $key->namedCurve();          // the OID of the curve
    $key->ECPoint();             // the point, as octets
    $key->curvePoint();          // [x, y] as decimal strings
    $key->curvePointOctets();    // [x, y] as octets
    $key->isCompressed();
    ```

    `curvePoint()` on a compressed point throws: decompression is not implemented. Ask `isCompressed()`
    first if the material is not yours.

    `ECPublicKey::fromCoordinates()` builds one from `x`, `y` and a curve, when you hold the coordinates
    rather than the encoded point. `EC\ECConversion` converts between the forms the specifications use —
    bit string, octet string and integer — which is what you need when bridging to a library that spells
    them differently.

=== "Ed25519 and Ed448"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\RFC8410\Curve25519\Ed25519PublicKey;

    /** @var Ed25519PublicKey $key */
    $key = $publicKeyInfo->publicKey();

    $key->subjectPublicKey();   // the BitString
    ```

An algorithm the library does not know raises `RuntimeException` from `publicKey()`. The container still
decoded, so `algorithmIdentifier()` tells you what you were handed.

## Verifying with one

Verification takes the `PublicKeyInfo`, not the inner key:

```php
$certificate->verify($issuerCertificate->tbsCertificate()->subjectPublicKeyInfo());
```

See [The crypto engine](the-crypto-engine.md).

!!! warning "`verify()` is not validation"

    `Certificate::verify()` answers one question: was this certificate signed by the key you passed? It
    says nothing about whether that key belongs to anyone you trust, whether the certificate is in date,
    or whether its issuer was allowed to sign it. Those are
    [path validation](../certification-paths/validating-a-path.md).
