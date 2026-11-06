---
description: Reading a private key in any of the formats OpenSSL writes, and what each key type gives you.
---

# Private keys

`PrivateKeyInfo` is the PKCS #8 container — an `OneAsymmetricKey`, after RFC 5958 — and the type every
`sign()` in the library takes.

## Reading one

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;

$privateKeyInfo = PrivateKeyInfo::fromPEM(PEM::fromFile('key.pem'));
$privateKeyInfo = PrivateKeyInfo::fromDER($der);
```

`fromPEM()` accepts three labels and normalises the two legacy ones into the container:

| PEM label | What it holds | Read as |
|---|---|---|
| `PRIVATE KEY` | PKCS #8, the modern format | decoded directly |
| `RSA PRIVATE KEY` | PKCS #1, what `openssl genrsa` used to write | wrapped |
| `EC PRIVATE KEY` | SEC 1, what `openssl ecparam -genkey` writes | wrapped |

Any other label — `ENCRYPTED PRIVATE KEY` among them — throws `UnexpectedValueException`. The library has
no password-based key derivation; see [Textual encoding (PEM)](../pem/README.md#what-is-refused).

To generate one to read:

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out key.pem   # PRIVATE KEY
openssl genpkey -algorithm ED25519 -out ed.pem                              # PRIVATE KEY
```

## What the container gives you

```php
$privateKeyInfo->algorithmIdentifier();   // what kind of key this is
$privateKeyInfo->privateKeyData();        // the inner structure, still encoded
$privateKeyInfo->privateKey();            // the inner structure, decoded
$privateKeyInfo->publicKeyInfo();         // the matching PublicKeyInfo
$privateKeyInfo->version();
$privateKeyInfo->toPEM()->string();
```

`publicKeyInfo()` returns the public key carried in the container when there is one, and derives it from
the private key otherwise. It is how you get the `PublicKeyInfo` a certificate or a certification
request needs:

```php
$tbsCertificate = TBSCertificate::create(
    $subject,
    $privateKeyInfo->publicKeyInfo(),   // here
    $issuer,
    $validity
);
```

## The key inside

`privateKey()` returns the algorithm-specific structure, decoded from `privateKeyData()`:

=== "RSA"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\RSA\RSAPrivateKey;

    /** @var RSAPrivateKey $key */
    $key = $privateKeyInfo->privateKey();

    $key->modulus();          // decimal string: it does not fit in an int
    $key->publicExponent();
    $key->privateExponent();
    $key->prime1();
    $key->prime2();
    $key->exponent1();
    $key->exponent2();
    $key->coefficient();
    ```

=== "Elliptic curve"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\EC\ECPrivateKey;

    /** @var ECPrivateKey $key */
    $key = $privateKeyInfo->privateKey();

    $key->hasNamedCurve();
    $key->namedCurve();          // the OID of the curve
    $key->privateKeyOctets();
    $key->publicKey();           // ECPublicKey, when the structure carries it
    ```

    !!! note "OpenSSL strips the curve, RFC 5915 requires it"

        OpenSSL drops the named curve from the inner `ECPrivateKey` when it wraps it into a
        `PrivateKeyInfo`, although RFC 5915 says the parameters must always be there. The library puts it
        back from the algorithm identifier of the container, so `namedCurve()` answers either way.

=== "Ed25519 and Ed448"

    ```php
    use SpomkyLabs\Pki\CryptoTypes\Asymmetric\RFC8410\Curve25519\Ed25519PrivateKey;

    /** @var Ed25519PrivateKey $key */
    $key = $privateKeyInfo->privateKey();

    $key->privateKeyData();
    $key->publicKey();
    ```

    RFC 8410 encodes the key as an `OCTET STRING` inside the `privateKey` `OCTET STRING`, so the material
    is doubly wrapped. The library unwraps both.

An algorithm the library does not know raises `RuntimeException` from `privateKey()`, with the algorithm
name in the message. The container itself still decoded, so `algorithmIdentifier()` and
`privateKeyData()` work: you can inspect what you were handed before giving up on it.

## Writing one

```php
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;

$privateKeyInfo = PrivateKeyInfo::fromPrivateKey($rsaPrivateKey);

file_put_contents('key.pem', $privateKeyInfo->toPEM()->string());
echo $privateKeyInfo->toDER();
```

Each key class also writes its own legacy format, if that is what you need:

```php
$rsaPrivateKey->toPEM()->string();   // -----BEGIN RSA PRIVATE KEY-----
$ecPrivateKey->toPEM()->string();    // -----BEGIN EC PRIVATE KEY-----
```

!!! warning "A private key in a variable is a private key on a core dump"

    The library holds key material as PHP strings and makes no attempt to wipe them: PHP gives no way to.
    Read keys from a path only your process can read, do not log the objects —
    `var_dump($privateKeyInfo)` prints the key — and prefer passing the `PrivateKeyInfo` around to
    re-reading the file.
