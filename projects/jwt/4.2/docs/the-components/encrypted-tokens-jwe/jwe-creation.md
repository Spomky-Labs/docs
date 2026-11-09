# JWE creation

The computation of a JWE is done by the `JWEBuilder` object. This object requires an algorithm manager with both key encryption and content encryption algorithms.

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Encryption\Algorithm\KeyEncryption\A256KW;
use Jose\Component\Encryption\Algorithm\ContentEncryption\A256CBCHS512;
use Jose\Component\Encryption\JWEBuilder;

// The algorithm manager with both key encryption and content encryption algorithms.
$algorithmManager = new AlgorithmManager([
    new A256KW(),        // Key Encryption Algorithm
    new A256CBCHS512(),  // Content Encryption Algorithm
]);

// We instantiate our JWE Builder.
$jweBuilder = new JWEBuilder($algorithmManager);
```

!!! danger

    Compression is not recommended. Please avoid its use. See [RFC8725](https://datatracker.ietf.org/doc/html/rfc8725#section-3.6) for more information.

Now let's create our first JWE object.

```php
use Jose\Component\Core\JWK;

// Our key: 256 bits, the key size of A256KW.
$jwk = new JWK([
    'kty' => 'oct',
    'k' => 'lX2B8De7F0jmDDlg52fp-Exeen2OUMxKxt2pZG7JMcI',
]);

// The payload we want to encrypt. It MUST be a string.
$payload = json_encode([
    'iat' => time(),
    'nbf' => time(),
    'exp' => time() + 3600,
    'iss' => 'My service',
    'aud' => 'Your application',
]);

$jwe = $jweBuilder
    ->create()              // We want to create a new JWE
    ->withPayload($payload) // We set the payload
    ->withSharedProtectedHeader([
        'alg' => 'A256KW',        // Key Encryption Algorithm
        'enc' => 'A256CBC-HS512', // Content Encryption Algorithm
    ])
    ->addRecipient($jwk)    // We add a recipient (a shared key or public key).
    ->build();              // We build it
```

The key must suit the key encryption algorithm, its size included, or `build()` throws. See the [key requirements](encryption-algorithms.md#key-requirements).

## Static key agreement (ECDH-SS)

The `ECDH-SS*` algorithms derive the agreement key from two **static** keys: no ephemeral key pair is generated, so no `epk` header parameter is added to the token and the recipient has to know the public key of the sender.

Give the private key of the sender to the builder with `withSenderKey()`:

```php
$jwe = $jweBuilder
    ->create()
    ->withPayload($payload)
    ->withSharedProtectedHeader([
        'alg' => 'ECDH-SS',
        'enc' => 'A128CBC-HS256',
    ])
    ->withSenderKey($senderPrivateKey)              // Your own private key
    ->addRecipient($recipientPublicKey)             // The key of the recipient
    ->build();
```

The sender key does not add a recipient, so it may be set before or after `addRecipient()`. It is checked by `build()`, once the recipients and the content encryption algorithm are known. A direct static key agreement without a sender key fails with `The sender key shall be set`.

!!! info

    The decryption side needs both keys too. See [JWE Loading](jwe-loading.md#static-key-agreement) for the order in which to pass them: since 4.2.7, both orders work.

## Header parameters

[RFC 7516 section 7.2.1](https://datatracker.ietf.org/doc/html/rfc7516#section-7.2.1) requires the header parameter names of the shared protected header, the shared unprotected header and the per-recipient headers to be **disjoint**. The builder rejects a token that would repeat a parameter across two of those locations.

The parameters computed by the key encryption algorithm itself — `epk`, `iv`, `tag`, `p2s`, `p2c`… — are filtered out of the per-recipient header when you already set them in a shared header, so setting e.g. `p2c` in the shared protected header of a multi-recipient `PBES2` token is safe.

## Serialization

Great! If everything is fine you will get a JWE object with one recipient. We want to send it to the audience. Before that, it must be serialized.

We will use the compact serialization mode. This is the most common mode as it is URL safe and very compact. Perfect for a use in a web context!

```php
use Jose\Component\Encryption\Serializer\CompactSerializer;

$serializer = new CompactSerializer(); // The serializer

$token = $serializer->serialize($jwe, 0); // We serialize the recipient at index 0 (we only have one recipient).
```

All good! The variable `$token` now contains a string that should be something like that:

```php
eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIn0.-rH3aFiivrg3ptfnhqmGZI-RHftx1Rr18QIUA5n-lwp4vWmCyCErrnaMP6deJYIgA1vyKPTf5wTj5s0970j1FqHgiH6Wqfn-.1aQIEld9RxZCIBg63w85jw.qOJnjgw3NP56YzG6Y1w4X-Yvppswj-skID_j5v3c4l7zsmk5b2UYXbPqVSJZDLs7aRgWYHV0g25Xx1Jti_IKb6hJ2mfwTnnHaccVT9Q5AxfRqId8pUjYnmovKxauaPquy2-W0py86sU2NidjO5QqQQ.aANQ4-I5uhEZ5C_CB66hKSTQ2vl6YShRo3txjS90_6M
```
