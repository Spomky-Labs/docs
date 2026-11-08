# JWE loading

Encrypted tokens are loaded by a serializer or the serializer manager and decrypted by the `JWEDecrypter` object. This JWEDecrypter object requires an algorithm manager with both key encryption and content encryption algorithms.

In the following example, we will use the same assumptions as the ones used during the [JWE Creation process](jwe-creation.md).

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Encryption\Algorithm\KeyEncryption\A256KW;
use Jose\Component\Encryption\Algorithm\ContentEncryption\A256CBCHS512;
use Jose\Component\Encryption\JWEDecrypter;

// The algorithm manager with both key encryption and content encryption algorithms.
$algorithmManager = new AlgorithmManager([
    new A256KW(),        // Key Encryption Algorithm
    new A256CBCHS512(),  // Content Encryption Algorithm
]);

// We instantiate our JWE Decrypter.
$jweDecrypter = new JWEDecrypter($algorithmManager);
```

Now we can try to deserialize and decrypt the input we receive. We will continue with the result we got during the JWE creation section.

!!! danger

    We do not check header parameters here, but it is very important to do it. This step is described in the [Header Checker](../header-checker.md) section.

```php
<?php

use Jose\Component\Core\JWK;
use Jose\Component\Encryption\Serializer\JWESerializerManager;
use Jose\Component\Encryption\Serializer\CompactSerializer;

// Our key.
$jwk = new JWK([
    'kty' => 'oct',
    'k' => 'lX2B8De7F0jmDDlg52fp-Exeen2OUMxKxt2pZG7JMcI', // A 256-bit key, as A256KW expects
]);

// The serializer manager. We only use the JWE Compact Serialization Mode.
$serializerManager = new JWESerializerManager([
    new CompactSerializer(),
]);

// The input we want to decrypt
$token = 'eyJhbGciOiJBMjU2S1ciLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIn0.-rH3aFiivrg3ptfnhqmGZI-RHftx1Rr18QIUA5n-lwp4vWmCyCErrnaMP6deJYIgA1vyKPTf5wTj5s0970j1FqHgiH6Wqfn-.1aQIEld9RxZCIBg63w85jw.qOJnjgw3NP56YzG6Y1w4X-Yvppswj-skID_j5v3c4l7zsmk5b2UYXbPqVSJZDLs7aRgWYHV0g25Xx1Jti_IKb6hJ2mfwTnnHaccVT9Q5AxfRqId8pUjYnmovKxauaPquy2-W0py86sU2NidjO5QqQQ.aANQ4-I5uhEZ5C_CB66hKSTQ2vl6YShRo3txjS90_6M';

// We try to load the token.
$jwe = $serializerManager->unserialize($token);

// We decrypt the token. This method does NOT check the header.
$success = $jweDecrypter->decryptUsingKey($jwe, $jwk, 0);
```

OK so if no exception is thrown, then your token is loaded and the payload correctly decrypted.

## JWELoader object

To avoid duplication of code lines, you can create a `JWELoader` object. This object contains a serializer, a decrypter and an optional header checker (highly recommended).

In the following example, the `JWELoader` object will try to unserialize the token `$token`, check the header parameters and decrypt with the key `$key`.

If the decryption succeeded, the variable `$recipient` will be set with the recipient index and should be in case of multiple recipients. The method returns the JWE object.

```php
<?php

use Jose\Component\Encryption\JWELoader;

$jweLoader = new JWELoader(
    $serializerManager,
    $jweDecrypter,
    $headerCheckerManager
);

$jwe = $jweLoader->loadAndDecryptWithKey($token, $key, $recipient);
```

In case you use a key set, you can use the method `loadAndDecryptWithKeySet`.

### Maximum number of recipients

A token in the JSON General serialization carries as many recipients as its sender wants, and the loader tries them one after the other. Since 4.2.6, the loader accepts the maximum number of recipients of a token as a fourth argument of its constructor: a token with more recipients is rejected before any of them is processed.

```php
<?php

use Jose\Component\Encryption\JWELoader;

$jweLoader = new JWELoader(
    $serializerManager,
    $jweDecrypter,
    $headerCheckerManager,
    10 // The maximum number of recipients of a token
);
```

The value must be a positive integer. Without it, the number of recipients is not limited, as before 4.2.6. Set it when the loader accepts the JSON General serialization (`jwe_json_general`) from senders you do not trust: 10 is enough for the tokens met in practice. The compact and JSON Flattened serializations always carry exactly one recipient.

A token with too many recipients fails like any other token: the loader throws `Unable to load and decrypt the token.`, and the previous exception says that the token has too many recipients.

!!! info

    That argument is not declared in the signature of the constructor yet: it is read with `func_num_args()`/`func_get_arg(3)`, so that classes extending the loader keep working. It will be declared in 5.0, with 10 as its default value. `JWELoaderFactory` does not pass it in 4.2: create the loader yourself to set it.

Since 4.2.6, the recipients of a token also share the iteration count cap of the `PBES2-*` algorithms: in a token with N recipients, a PBES2 recipient may request at most `max_count / N` iterations, `max_count` being the third argument of the constructor of the algorithm (1,000,000 by default). A recipient that requests more is not decrypted. Tokens with a single recipient are not affected, and tokens built with the default count of 4,096 iterations are still decrypted up to 244 recipients.

## JWELoaderFactory object

The `JWELoaderFactory` object is able to create `JWELoader` objects on demand. It requires the following factories:

* `JWESerializerManagerFactory`
* `JWEDecrypterFactory`
* `HeaderCheckerManagerFactory` (optional, see below)

```php
<?php

use Jose\Component\Encryption\JWELoaderFactory;

$jweLoaderFactory = new JWELoaderFactory(
    $jweSerializerManagerFactory,
    $jweDecrypterFactory,
    $headerCheckerManagerFactory
);

$jweLoader = $jweLoaderFactory->create(
    ['jwe_compact'],           // List of serializer aliases
    ['A256KW', 'A256CBCHS512'], // List of encryption algorithm aliases (both key and content)
    ['alg', 'enc']             // Optional list of header checker aliases
);
```

### Without a header checker manager factory

A factory created with `null` instead of a `HeaderCheckerManagerFactory` can only create loaders that check no header parameter, not even those listed in `crit`. Since 4.2.7, its `create()` method throws an `InvalidArgumentException` (`Header checkers were requested, but no header checker manager factory is available.`) when header checker aliases are given. It used to ignore them and return a loader that checked nothing. With an empty list, it still returns a loader without header checker manager.

The exception is thrown when the loader is created, not when a token is loaded. To fix it, give the factory a `HeaderCheckerManagerFactory`. With the Symfony bundle, use the [factory services of the bundle](../../the-symfony-bundle/encrypted-tokens/jwe-decryption.md#jwe-loader-service) rather than registering the library factories with autowiring, which leaves this argument `null`.

## Header validation

[RFC 7516 section 7.2.1](https://datatracker.ietf.org/doc/html/rfc7516#section-7.2.1) requires the header parameter names of the three locations — shared protected header, shared unprotected header and per-recipient header — to be **disjoint**. The `JWEDecrypter` enforces it and rejects a token that repeats a parameter across two locations.

Two consequences are worth knowing:

* the protected header always wins. An unprotected parameter can never override an integrity protected one, `alg` and `enc` included;
* `alg` and `enc` are never read from the **shared unprotected** header. That header is not covered by the AAD and, unlike the per-recipient header, nothing requires those parameters to be located there. Put them in the shared protected header.

!!! warning

    This is enforced since 4.2. Tokens built like the [RFC 7520](https://datatracker.ietf.org/doc/html/rfc7520) sections 5.11 and 5.12 vectors are still parsed, but are no longer decrypted. See the [migration guide](../../migration/from-v4.1-to-v4.2.md#stricter-header-validation-on-decryption).

This validation is not a substitute for the [Header Checker](../header-checker.md): it only checks where the parameters are, not what they contain.

## Static key agreement

The `ECDH-SS*` algorithms derive the agreement key from two **static** keys, so no `epk` header parameter is present in the token and the decrypter must be given both keys.

The order below swaps the roles compared to the [creation side](jwe-creation.md#static-key-agreement-ecdh-ss): the key used to decrypt is the **public key of the sender**, and the additional key is the **private key of the recipient**.

```php
$success = $jweDecrypter->decryptUsingKey(
    $jwe,
    $senderPublicKey,     // The key of the sender
    0,
    $recipientPrivateKey  // Your own private key
);
```

Since 4.2.7, the other order works too: your private key as the key used to decrypt, and the public key of the sender as the additional key. Before 4.2.7, that order did not decrypt genuine tokens. The agreement is computed from the two static keys only, whichever of them is the private one, and an `epk` header parameter found in an `ECDH-SS*` token is never read.

## Understanding failures

When a token cannot be loaded or decrypted, the loaders and the serializer manager chain the last error met along the way as the previous exception:

```php
<?php

use Throwable;

try {
    $jwe = $jweLoader->loadAndDecryptWithKeySet($token, $jwkset, $recipient);
} catch (Throwable $throwable) {
    $this->logger->debug($throwable->getMessage(), [
        'cause' => $throwable->getPrevious()?->getMessage(),
    ]);

    throw $throwable;
}
```

`JWEDecrypter` returns a boolean and cannot throw without changing that contract, so its per-key failures are reported through a callable it accepts as an additional argument. It is called once per key that failed:

```php
$success = $jweDecrypter->decryptUsingKeySet(
    $jwe,
    $jwkset,
    0,
    $jwk,        // Set with the key that succeeded
    $senderKey,  // Static key agreement only, see "Static Key Agreement" below
    static function (Throwable $throwable): void {
        // Called for each key that could not decrypt the token.
    }
);
```

!!! info

    That callable is not declared in the signature of `decryptUsingKeySet()` yet — it is read with `func_num_args()`/`func_get_arg(5)` so that classes extending the decrypter keep working. It will become part of the signature in 5.0.

