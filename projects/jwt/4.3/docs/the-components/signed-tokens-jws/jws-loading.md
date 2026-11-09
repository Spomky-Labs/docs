# JWS loading

Signed tokens are loaded by a serializer or the serializer manager and verified by the `JWSVerifier` object. This JWSVerifier object just requires an algorithm manager.

## Serializer and verifier

In the following example, we will try to load a signed token. We will only use the `HS256` algorithm.

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Signature\Algorithm\HS256;
use Jose\Component\Signature\JWSVerifier;

// The algorithm manager with the HS256 algorithm.
$algorithmManager = new AlgorithmManager([
    new HS256(),
]);

// We instantiate our JWS Verifier.
$jwsVerifier = new JWSVerifier(
    $algorithmManager
);
```

Now we can deserialize the input we receive and check the signature using our key. We will continue with the data we got in the JWS creation section.

!!! danger

    We do not check header parameters here, but it is very important to do it. This step is described in the [Header Checker section](../header-checker.md).

```php
<?php

use Jose\Component\Core\JWK;
use Jose\Component\Signature\Serializer\JWSSerializerManager;
use Jose\Component\Signature\Serializer\CompactSerializer;

// Our key.
$jwk = new JWK([
    'kty' => 'oct',
    'k' => 'dzI6nbW4OcNF-AtfxGAmuyz7IpHRudBI0WgGjZWgaRJt6prBn3DARXgUR8NVwKhfL43QBIU2Un3AvCGCHRgY4TbEqhOi8-i98xxmCggNjde4oaW6wkJ2NgM3Ss9SOX9zS3lcVzdCMdum-RwVJ301kbin4UtGztuzJBeg5oVN00MGxjC2xWwyI0tgXVs-zJs5WlafCuGfX1HrVkIf5bvpE0MQCSjdJpSeVao6-RSTYDajZf7T88a2eVjeW31mMAg-jzAWfUrii61T_bYPJFOXW8kkRWoa1InLRdG6bKB9wQs9-VdXZP60Q4Yuj_WZ-lO7qV9AEFrUkkjpaDgZT86w2g',
]);

// The serializer manager. We only use the JWS Compact Serialization Mode.
$serializerManager = new JWSSerializerManager([
    new CompactSerializer(),
]);

// The input we want to check
$token = 'eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1MDc4OTY5OTIsIm5iZiI6MTUwNzg5Njk5MiwiZXhwIjoxNTA3OTAwNTkyLCJpc3MiOiJNeSBzZXJ2aWNlIiwiYXVkIjoiWW91ciBhcHBsaWNhdGlvbiJ9.eycp9PTdgO4WA-68-AMoHPwsKDr68NhjIQKz4lUkiI0';

// We try to load the token.
$jws = $serializerManager->unserialize($token);

// We verify the signature. This method does NOT check the header.
// The arguments are:
// - The JWS object,
// - The key or the key set,
// - The index of the signature to check.
$result = $jwsVerifier->verify($jws, $jwk, 0);
```

`verify()` returns a `VerificationResult`:

```php
$result->isVerified();        // bool — true when the signature is valid
$result->getSignatureIndex(); // int — the index of the signature that was checked
$result->getKey();            // ?JWK — the key that verified it, null on failure
```

If the signature is valid, you can then check the claims (if any) using the claim checker manager.

The second argument accepts a `JWK` as well as a `JWKSet`; when a key set is given, every key is tried until one verifies the signature, and `getKey()` tells you which one did.

!!! info

    `verifyWithKey()` still exists and is not deprecated: it takes a single key and returns a boolean, with no output parameter. `verifyWithKeySet()`, which wrote the successful key into a variable of the caller, is deprecated since 4.3 in favour of `verify()`.

## JWSLoader object

To avoid duplication of code lines, you can create a `JWSLoader` object. This object contains a serializer, a verifier and an optional header checker (highly recommended).

In the following example, the `JWSLoader` object will try to unserialize the token `$token`, check the header parameters and verify the signature with the key `$jwk`. The third argument corresponds to the detached payload (`null` by default).

```php
<?php

use Jose\Component\Signature\JWSLoader;

$jwsLoader = new JWSLoader(
    $serializerManager,
    $jwsVerifier,
    $headerCheckerManager
);

$result = $jwsLoader->loadAndVerify($token, $jwk, $payload);

$jws       = $result->getJws();
$signature = $result->getSignatureIndex(); // Useful with multiple signatures
$key       = $result->getKey();            // The key that verified the signature
```

`loadAndVerify()` accepts a `JWK` as well as a `JWKSet`, and throws when the token cannot be loaded or verified.

!!! warning

    `loadAndVerifyWithKey()` and `loadAndVerifyWithKeySet()` wrote the signature index into a variable of the caller. They are deprecated since 4.3 and removed in 5.0: use `loadAndVerify()`, which carries that index in its result. See the [migration guide](../../migration/from-v4.2-to-v4.3.md#result-objects-instead-of-output-parameters).

### Maximum number of signatures

A token in the JSON General serialization carries as many signatures as its sender wants, and the loader tries them one after the other. The loader accepts the maximum number of signatures of a token as a fourth argument of its constructor (since 4.2.6): a token with more signatures is rejected before any of them is processed.

```php
<?php

use Jose\Component\Signature\JWSLoader;

$jwsLoader = new JWSLoader(
    $serializerManager,
    $jwsVerifier,
    $headerCheckerManager,
    JWSLoader::DEFAULT_MAX_SIGNATURES // 10
);
```

The value must be a positive integer. The compact and JSON Flattened serializations always carry exactly one signature, so the limit matters when the loader accepts the JSON General serialization (`jws_json_general`). A token with too many signatures fails like any other token: `loadAndVerify()` throws, and the previous exception says that the token has too many signatures.

`JWSLoaderFactory::create()` takes the same value as a fourth argument (see [below](#jwsloaderfactory-object)), and the bundle as the [`max_signatures`](../../the-symfony-bundle/signed-tokens/jws-verification.md#maximum-number-of-signatures) option of a loader.

!!! warning

    Without that argument, the number of signatures is not limited. Since 4.3, loading a token with more than 10 signatures without a maximum is deprecated: in 5.0, such a token is rejected unless a higher maximum is set. Setting a maximum, higher or lower than 10, silences the notice. The argument is read with `func_num_args()`/`func_get_arg(3)` until 5.0 declares it, with `JWSLoader::DEFAULT_MAX_SIGNATURES` (10) as its default value.

## JWSLoaderFactory object

The `JWSLoaderFactory` object is able to create `JWSLoader` objects on demand. It requires the following factories:

* `JWSSerializerManagerFactory`
* `JWSVerifierFactory`
* `HeaderCheckerManagerFactory` (required in 5.0, see below)

```php
<?php

use Jose\Component\Signature\JWSLoaderFactory;

$jwsLoaderFactory = new JWSLoaderFactory(
    $jwsSerializerManagerFactory,
    $jwsVerifierFactory,
    $headerCheckerManagerFactory
);

$jwsLoader = $jwsLoaderFactory->create(
    ['jws_compact'], // List of serializer aliases
    ['HS256'],       // List of signature algorithm aliases
    ['alg'],         // Optional list of header checker aliases
    10               // Optional maximum number of signatures of a token
);
```

### Without a header checker manager factory

A factory created with `null` instead of a `HeaderCheckerManagerFactory` can only create loaders that check no header parameter, not even those listed in `crit`. Since 4.2.7, its `create()` method throws an `InvalidArgumentException` (`Header checkers were requested, but no header checker manager factory is available.`) when header checker aliases are given, instead of ignoring them. With an empty list, it still returns a loader without header checker manager.

!!! warning

    Since 4.3, creating a `JWSLoaderFactory` without a header checker manager factory is deprecated, and the argument is required in 5.0. Pass a `HeaderCheckerManagerFactory` that has the `JWSTokenSupport` [token type support](../header-checker.md#header-checker-manager-factory): without it, the loaders refuse every token (`Unsupported token type.`). With the Symfony bundle, use the [factory services of the bundle](../../the-symfony-bundle/signed-tokens/jws-verification.md#jws-loader-service): registering the library factories with autowiring leaves this argument `null`.

## Understanding failures

When a token cannot be loaded or verified, the loaders and the serializer manager chain the last error met along the way as the previous exception. The message of the outer exception stays generic on purpose — it is the one you may safely show — while the cause tells you what actually happened:

```php
<?php

use Jose\Component\Core\Exception\JoseException;

try {
    $result = $jwsLoader->loadAndVerify($token, $jwkset);
} catch (JoseException $throwable) {
    $this->logger->debug($throwable->getMessage(), [
        'cause' => $throwable->getPrevious()?->getMessage(),
    ]);

    throw $throwable;
}
```

Every exception thrown by the framework implements `JoseException`, so a single catch block handles any failure. Each of them extends the SPL exception that was thrown at that place before 4.3, hence catch blocks written for previous versions keep matching.

A token rejected for its size or its depth has a `JsonBoundExceededException` further down the chain, whose message names the bound: see [Rejections for a bound](../../advanced-topics/serialization.md#rejections-for-a-bound).

`JWSVerifier` reports a failure through its result rather than an exception, so the per-key failures it meets while trying a key set are reported through an optional callable. It is called once per key that failed:

```php
$result = $jwsVerifier->verify(
    $jws,
    $jwkset,
    0,
    null, // Detached payload
    static function (Throwable $throwable): void {
        // Called for each key that could not verify the signature.
    }
);
```

