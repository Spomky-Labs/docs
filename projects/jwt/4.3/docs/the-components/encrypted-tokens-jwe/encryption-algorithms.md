# Encryption algorithms

This framework comes with several encryption algorithms. These algorithms are in the following namespaces:

* `Jose\Component\Encryption\Algorithm\KeyEncryption`: key encryption algorithms
* `Jose\Component\Encryption\Algorithm\ContentEncryption`: content encryption algorithms

## Main algorithms

### Key encryption

!!! info

    `spomky-labs/aes-key-wrap` is required for \*KW algorithms

| Algorithm | Additional header parameter |
|---|---|
| A128KW<br>A192KW<br>A256KW | No |
| A128GCMKW<br>A192GCMKW<br>A256GCMKW | `iv`:  (initialization vector) this value is the base64url-encoded representation of the 96-bit IV value used for the key encryption operation.<br>`tag`: (authentication tag) the value is the base64url-encoded representation of the 128-bit Authentication Tag value resulting from the key encryption operation. |
| dir | No |
| ECDH-ES<br>ECDH-ES+A128KW<br>ECDH-ES+A192KW<br>ECDH-ES+A256KW | `epk`: (ephemeral public key) value created by the originator. |
| ECDH-SS<br>ECDH-SS+A128KW<br>ECDH-SS+A192KW<br>ECDH-SS+A256KW | No |
| PBES2-HS256+A128KW<br>PBES2-HS384+A192KW<br>PBES2-HS512+A256KW | `p2s`: (PBES2 salt input) encodes a Salt Input value, which is used as part of the PBKDF2 salt value.<br>`p2c`: (PBES2 count) contains the PBKDF2 iteration count, represented as a positive JSON integer. |
| RSA1_5<br>RSA-OAEP<br>RSA-OAEP-256 |  |

!!! warning

    Please note that the additional header parameters **MUST** be present and **MUST** be understood. Depending on the algorithm you use, you may be required to check headers BEFORE the decryption operation. Please create a [custom Header Checker](../header-checker.md) for theses parameters.

### Content encryption

| Algorithm                                                    | Namespace                                                             |
| ------------------------------------------------------------ | --------------------------------------------------------------------- |
|A128GCM<br>A192GCM<br>A256GCM| `Jose\Component\Encryption\Algorithm\ContentEncryption` |
|A128CBC-HS256<br>A192CBC-HS384<br>A256CBC-HS512| `Jose\Component\Encryption\Algorithm\ContentEncryption` |

!!! info

    Since 4.3, the AES-CBC-HMAC algorithms compute the authentication tag of a token that has an AAD as RFC 7518 requires. Tokens of that kind issued by 4.3 cannot be decrypted by earlier versions. See [AES-CBC-HMAC tokens with an AAD](../../advanced-topics/encrypted-tokens/additional-authentication-data-aad.md#aes-cbc-hmac-tokens-with-an-aad).

!!! danger

    The algorithm `RSA1_5` is deprecated due to known [security vulnerability](https://en.wikipedia.org/wiki/Adaptive_chosen-ciphertext_attack).

    The algorithms `ECDH-ES*` are not recommended unless used with the `OKP` key type.

### The `RSA1_5` algorithm

Since 4.3, `RSA1_5` lives in its own package, so that enabling an algorithm whose padding is vulnerable to the Bleichenbacher adaptive chosen-ciphertext attack is an explicit and auditable decision:

```bash
composer require web-token/jwt-rsa15
```

```php
<?php

use Jose\Rsa15\KeyEncryption\RSA15;
```

!!! warning

    `Jose\Component\Encryption\Algorithm\KeyEncryption\RSA15` still works — it is an empty subclass of the new class — but it is deprecated since 4.3 and removed in 5.0. In the Symfony Bundle, the configuration alias is unchanged: `RSA1_5` still names the algorithm.

### Curves supported by the key agreement algorithms

The `ECDH-ES*` and `ECDH-SS*` algorithms accept:

* `EC` keys using the `P-256`, `P-384`, `P-521`, `BP-256`, `BP-384` or `BP-512` curve,
* `OKP` keys using the `X25519` curve (SODIUM extension, or OpenSSL on PHP 8.4+) or the `X448` curve (PHP 8.4+ is required, OpenSSL; since 4.3).

The `BP-*` curves are the Brainpool curves. They are part of the core library and do not require the experimental package. Please read the [warning about their interoperability](../key-jwk-and-key-set-jwkset/key-management.md#elliptic-curve-key-pair) before using them.

## Key requirements

The algorithms check the keys they are given and the keys a token carries. A key that does not meet the requirements below makes `build()` throw. On decryption, it is not used and the decrypter moves on to the next key of the key set: a token that no key can decrypt is rejected as usual.

### Direct encryption (`dir`)

With `dir`, the `oct` key is the content encryption key (CEK) itself, so its size is set by the content encryption algorithm:

| Content encryption algorithm | Key size |
|---|---|
| A128GCM<br>A192GCM<br>A256GCM | 128 bits<br>192 bits<br>256 bits |
| A128CBC-HS256<br>A192CBC-HS384<br>A256CBC-HS512 | 256 bits<br>384 bits<br>512 bits |

The AES-CBC-HMAC algorithms need twice the size their name suggests, as half of the key authenticates the content and the other half encrypts it: a 128-bit key is too short for `A128CBC-HS256`. With `dir`, the `alg` member of the key, when present, names the content encryption algorithm:

```php
use Jose\Component\KeyManagement\JWKFactory;

$jwk = (new JWKFactory())->oct(512, ['alg' => 'A256CBC-HS512', 'use' => 'enc']);
```

* Since 4.2.6, a shorter key is refused: `build()` throws `Invalid CEK size`, and the decrypter does not decrypt with it.
* Since 4.3, a longer key is deprecated, to build and to decrypt, and 5.0 refuses it. Only its first bytes are used, as many as the CEK has: replace the key with them, and the tokens already issued still decrypt.

!!! warning

    Since 4.3, building or decrypting a `dir` JWE that has neither a protected header nor an AAD is deprecated, and 5.0 refuses it. Such a token only exists in the JSON serializations, with `alg` and `enc` in the per-recipient header. Its content is then encrypted with an empty AAD, as AES-GCM key wrapping encrypts a key, so under a key used for both, one can pass for the other. Put `alg` and `enc` in the shared protected header; an `alg` member on each key also keeps it to one algorithm. Compact tokens always have a protected header.

### Encrypted key of the direct modes

`dir`, `ECDH-ES` and `ECDH-SS` transport no key: the encrypted key of the token is empty. Since 4.2.6, the decrypter refuses a token of these modes whose encrypted key is not empty. In the JSON serializations, an `encrypted_key` member set to `""` is still accepted. The tokens built by the library always leave it empty.

### AES key wrapping keys

`A128KW`, `A192KW`, `A256KW`, `A128GCMKW`, `A192GCMKW` and `A256GCMKW` need an `oct` key of exactly 128, 192 or 256 bits, as their name says. Generate it at random; never build it from a text secret or from an environment variable that may be empty:

```php
use Jose\Component\KeyManagement\JWKFactory;

$jwk = (new JWKFactory())->oct(256, ['alg' => 'A256KW', 'use' => 'enc']);
```

* Since 4.2.6, a shorter key, an empty one included, is refused with `Invalid key length.`, to wrap and to unwrap.
* Since 4.3, a longer key is deprecated, and 5.0 refuses it. Only its first 16, 24 or 32 bytes are used: replace the key with them, and the tokens already issued still decrypt.

The same goes for the experimental `A128CTR`, `A192CTR` and `A256CTR` (128, 192 and 256 bits) and `chacha20-poly1305` (256 bits) key encryption algorithms.

Since 4.3, the decrypter also checks the size of a key wrapped with AES Key Wrap (`A*KW`, `PBES2-*` and `ECDH-*+A*KW`) before unwrapping it: any size but the CEK size plus 64 bits is rejected with `Invalid encrypted key size`.

### RSA keys

Since 4.2.6, every RSA algorithm, the signature ones included, refuses a key beyond the limits of OpenSSL:

* a modulus longer than 16384 bits;
* a public exponent longer than the modulus;
* a public exponent longer than 64 bits when the modulus is longer than 3072 bits.

Every key that OpenSSL accepts is still accepted. Use keys of 2048 bits at least.

Since 4.2.6, `RSA-OAEP` and `RSA-OAEP-256` handle a single RSA block, as RFC 7518 requires:

* the CEK must fit in one block. With a key shorter than 2048 bits it may not: `RSA-OAEP-256` with a 1024-bit key and `A256CBC-HS512` throws `Message too long`;
* an encrypted key longer than the modulus is refused;
* since 4.3, an encrypted key shorter than the modulus is deprecated: it is still decrypted, and 5.0 refuses it. Conforming senders always produce an encrypted key as long as the modulus.

Since 4.3, the RSA public key operation, which encrypts with `RSA-OAEP`, `RSA-OAEP-256` and `RSA1_5`, is computed by OpenSSL: its cost no longer depends on the GMP or BCMath extension. Decryption is still computed in PHP, where GMP remains recommended.

### Ephemeral public key (`epk`)

With `ECDH-ES` and its `+A*KW` variants, the token carries the ephemeral public key of the sender in its `epk` header parameter. That key must be a point of the curve of the recipient key, with coordinates no longer than the size of the curve; otherwise the token is refused with `Unable to derive the key`. Since 4.2.6, these checks come before any costly computation, with or without the GMP extension.

Since 4.2.6, `ECDH-SS` refuses the same way a sender key on another curve than the recipient key.

### Key operations (`key_ops`)

When a key has a `key_ops` parameter, it must allow the operation the key is used for. Since 4.3, the operations are read according to the key management mode:

| Key management mode | To build a token | To decrypt a token |
|---|---|---|
| `dir` | `encrypt` | `decrypt` |
| `ECDH-ES`, `ECDH-SS` and their `+A*KW` variants | `deriveKey`, `deriveBits`, `encrypt` or `wrapKey` | `deriveKey`, `deriveBits`, `decrypt` or `unwrapKey` |
| The other algorithms | `encrypt`, `wrapKey` or `deriveKey` | `decrypt`, `unwrapKey` or `deriveBits` |

* With `dir`, the key encrypts the content. A key that only allows `wrapKey` or `deriveKey` to build, or `unwrapKey` or `deriveBits` to decrypt, still works but is deprecated, and 5.0 refuses it: add `encrypt` and `decrypt` to such keys, or remove their `key_ops` parameter.
* The key agreement algorithms accept both `deriveKey` and `deriveBits`, to build and to decrypt, as WebCrypto exports an ECDH key with either. Before 4.3, `deriveBits` only allowed decrypting and `deriveKey` only allowed building.

Keys without `key_ops` are not concerned.

## Experimental algorithms

The following algorithms are experimental and must not be used in production unless you know what you are doing. **They are proposed for testing purpose only.**

### Key encryption

| Algorithm | Description |
|---|---|
| A128CTR<br>A192CTR<br>A256CTR | AES CTR based encryption |
| Chacha20+Poly1305 | *Please note that this algorithm requires OpenSSL 1.1* |
| RSA-OAEP-384<br>RSA-OAEP-512 | Same algorithm as RSA-OAEP-256 but with SHA-384 and SHA-512 hashing functions |

### Content encryption

| Algorithm | Description |
|---|---|
| A128CCM-16-128<br>A128CCM-16-64<br>A128CCM-64-128<br>A128CCM-64-64<br>A256CCM-16-128<br>A256CCM-16-64<br>A256CCM-64-128<br>A256CCM-64-64 | AES-CCM based algorithms |

## How to use

These algorithms have to be used with the [Algorithm Manager](../algorithm-management-jwa.md).

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Encryption\Algorithm\KeyEncryption\A128KW;
use Jose\Component\Encryption\Algorithm\KeyEncryption\PBES2HS256A128KW;
use Jose\Component\Encryption\Algorithm\ContentEncryption\A128CBCHS256;

$algorithmManager = new AlgorithmManager([
    new A128KW(),
    new PBES2HS256A128KW(),
    new A128CBCHS256(),
]);
```

By default, `PBES2*` algorithms use the following parameter values:

* Salt size: 64 bytes (512 bits)
* Count: 4096&#x20;

You may need to use other values. This can be done during the instantiation of the algorithm:

Example with 16 bytes (128 bits) salt and 1024 counts:

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Encryption\Algorithm\KeyEncryption\PBES2HS256A128KW;

$algorithmManager = new AlgorithmManager([
    new PBES2HS256A128KW(16, 1024),
]);
```
