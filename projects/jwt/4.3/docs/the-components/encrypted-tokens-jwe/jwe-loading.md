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
$result = $jweDecrypter->decrypt($jwe, $jwk, 0);
```

`decrypt()` returns a `DecryptionResult`:

```php
$result->isDecrypted();       // bool
$result->getJwe();            // JWE — the decrypted token, carrying the payload
$result->getRecipientIndex(); // int
$result->getKey();            // ?JWK — the key that decrypted it, null on failure

$payload = $result->getJwe()->getPayload();
```

The second argument accepts a `JWK` as well as a `JWKSet`. JWE objects are immutable, so **the JWE you pass is left untouched**: read the decrypted one from the result.

!!! warning

    `decryptUsingKey()` and `decryptUsingKeySet()` wrote the payload into the JWE passed by reference. They are deprecated since 4.3 and removed in 5.0: use `decrypt()`. See the [migration guide](../../migration/from-v4.2-to-v4.3.md#result-objects-instead-of-output-parameters).

## JWELoader object

To avoid duplication of code lines, you can create a `JWELoader` object. This object contains a serializer, a decrypter and an optional header checker (highly recommended).

In the following example, the `JWELoader` object will try to unserialize the token `$token`, check the header parameters and decrypt with the key `$key`.

```php
<?php

use Jose\Component\Encryption\JWELoader;

$jweLoader = new JWELoader(
    $serializerManager,
    $jweDecrypter,
    $headerCheckerManager
);

$result = $jweLoader->loadAndDecrypt($token, $key);

$jwe       = $result->getJwe();
$recipient = $result->getRecipientIndex(); // Useful with multiple recipients
$payload   = $jwe->getPayload();
```

`loadAndDecrypt()` accepts a `JWK` as well as a `JWKSet`, and throws when the token cannot be loaded or decrypted.

!!! warning

    `loadAndDecryptWithKey()` and `loadAndDecryptWithKeySet()` wrote the recipient index into a variable of the caller. They are deprecated since 4.3 and removed in 5.0: use `loadAndDecrypt()`.

### Maximum number of recipients

A token in the JSON General serialization carries as many recipients as its sender wants, and the loader tries them one after the other. The loader accepts the maximum number of recipients of a token as a fourth argument of its constructor (since 4.2.6): a token with more recipients is rejected before any of them is processed.

```php
<?php

use Jose\Component\Encryption\JWELoader;

$jweLoader = new JWELoader(
    $serializerManager,
    $jweDecrypter,
    $headerCheckerManager,
    JWELoader::DEFAULT_MAX_RECIPIENTS // 10
);
```

The value must be a positive integer. The compact and JSON Flattened serializations always carry exactly one recipient, so the limit matters when the loader accepts the JSON General serialization (`jwe_json_general`). A token with too many recipients fails like any other token: `loadAndDecrypt()` throws, and the previous exception says that the token has too many recipients.

`JWELoaderFactory::create()` takes the same value as a fourth argument (see [below](#jweloaderfactory-object)), and the bundle as the [`max_recipients`](../../the-symfony-bundle/encrypted-tokens/jwe-decryption.md#maximum-number-of-recipients) option of a loader.

!!! warning

    Without that argument, the number of recipients is not limited. Since 4.3, loading a token with more than 10 recipients without a maximum is deprecated: in 5.0, such a token is rejected unless a higher maximum is set. Setting a maximum, higher or lower than 10, silences the notice. The argument is read with `func_num_args()`/`func_get_arg(3)` until 5.0 declares it, with `JWELoader::DEFAULT_MAX_RECIPIENTS` (10) as its default value.

Since 4.2.6, the recipients of a token also share the iteration count cap of the `PBES2-*` algorithms: in a token with N recipients, a PBES2 recipient may request at most `max_count / N` iterations, `max_count` being the third argument of the constructor of the algorithm (1,000,000 by default). A recipient that requests more is not decrypted. Tokens with a single recipient are not affected, and tokens built with the default count of 4,096 iterations are still decrypted up to 244 recipients.

## JWELoaderFactory object

The `JWELoaderFactory` object is able to create `JWELoader` objects on demand. It requires the following factories:

* `JWESerializerManagerFactory`
* `JWEDecrypterFactory`
* `HeaderCheckerManagerFactory` (required in 5.0, see below)

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
    ['alg', 'enc'],            // Optional list of header checker aliases
    10                         // Optional maximum number of recipients of a token
);
```

### Without a header checker manager factory

A factory created with `null` instead of a `HeaderCheckerManagerFactory` can only create loaders that check no header parameter, not even those listed in `crit`. Since 4.2.7, its `create()` method throws an `InvalidArgumentException` (`Header checkers were requested, but no header checker manager factory is available.`) when header checker aliases are given, instead of ignoring them. With an empty list, it still returns a loader without header checker manager.

!!! warning

    Since 4.3, creating a `JWELoaderFactory` without a header checker manager factory is deprecated, and the argument is required in 5.0. Pass a `HeaderCheckerManagerFactory` that has the `JWETokenSupport` [token type support](../header-checker.md#header-checker-manager-factory): without it, the loaders refuse every token (`Unsupported token type.`). With the Symfony bundle, use the [factory services of the bundle](../../the-symfony-bundle/encrypted-tokens/jwe-decryption.md#jwe-loader-service): registering the library factories with autowiring leaves this argument `null`.

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
$result = $jweDecrypter->decrypt(
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

use Jose\Component\Core\Exception\JoseException;

try {
    $result = $jweLoader->loadAndDecrypt($token, $jwkset);
} catch (JoseException $throwable) {
    $this->logger->debug($throwable->getMessage(), [
        'cause' => $throwable->getPrevious()?->getMessage(),
    ]);

    throw $throwable;
}
```

Every exception thrown by the framework implements `JoseException`, so a single catch block handles any failure. Each of them extends the SPL exception that was thrown at that place before 4.3, hence catch blocks written for previous versions keep matching.

A token rejected for its size or its depth has a `JsonBoundExceededException` further down the chain, whose message names the bound: see [Rejections for a bound](../../advanced-topics/serialization.md#rejections-for-a-bound).

`JWEDecrypter` reports a failure through its result rather than an exception, so the per-key failures it meets while trying a key set are reported through an optional callable. It is called once per key that failed:

```php
$result = $jweDecrypter->decrypt(
    $jwe,
    $jwkset,
    0,
    $senderKey, // Static key agreement only, see "Static Key Agreement" above
    static function (Throwable $throwable): void {
        // Called for each key that could not decrypt the token.
    }
);
```

