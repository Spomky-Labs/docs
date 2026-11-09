# From v4.2 to v4.3

This is a minor version upgrade: **your code keeps working**. Version 4.3 introduces no breaking change, but it is the version where 5.0 is prepared, so it carries a lot of deprecations. Each of them names its replacement, and the [summary table](#deprecation-summary) at the end lists them all. A few behaviours and return types change too: read [Behaviour changes](#behaviour-changes) before you upgrade.

Two algorithms move to their own packages. If your application enables `none` or `RSA1_5`, this is the only change that needs an entry in your `composer.json` — see [Dangerous algorithms](#dangerous-algorithms-move-to-their-own-packages).

If your application requires the packages one by one — `web-token/jwt-library`, `web-token/jwt-bundle`, `web-token/jwt-experimental`… — instead of `web-token/jwt-framework`, update them together, for example with `composer update "web-token/*" --with-all-dependencies`. The bundle and the experimental package of 4.3 require the library 4.3.

Coming from an earlier version, read the previous guides first: [From v4.1 to v4.2](from-v4.1-to-v4.2.md), then [From v4.0 to v4.1](from-v4.0-to-v4.1.md).

Version 4.3 also contains every fix of the 4.2 patch releases, up to 4.2.7. Some of them refuse keys or tokens that an earlier 4.2 release accepted: if you upgrade from a release before 4.2.7, read [Changes in the patch releases](from-v4.1-to-v4.2.md#changes-in-the-patch-releases) too.

## New features

### Every service has an interface

None of the main services was final and none of them had an interface: they could neither be relied upon as closed, nor be decorated.

Every service now implements an interface — `JWSBuilderInterface`, `JWSVerifierInterface`, `JWSLoaderInterface`, `JWEBuilderInterface`, `JWEDecrypterInterface`, `JWELoaderInterface`, `NestedTokenBuilderInterface`, `NestedTokenLoaderInterface`, `ClaimCheckerManagerInterface` and `HeaderCheckerManagerInterface` — and the library type-hints those interfaces internally, so a decorator can be injected anywhere a service is expected.

```php
<?php

use Jose\Component\Signature\JWSLoaderInterface;

final readonly class MyTokenReader
{
    public function __construct(
        private JWSLoaderInterface $jwsLoader, // Instead of the concrete JWSLoader
    ) {
    }
}
```

In the Symfony Bundle, each service is now aliased with its interface too, so `JWSBuilderInterface $myJwsBuilder` is autowired exactly as `JWSBuilder $myJwsBuilder` already was.

**Extending the concrete classes is deprecated.** They carry the `@final` annotation and their constructor raises a deprecation notice. Implement the interface or decorate the service instead.

### Result objects instead of output parameters

The verifiers, the decrypters, the loaders and the serializer managers used to write their secondary results — the key that verified a signature, the index of the recipient that could be decrypted, the name of the serializer — into variables of the caller. Such methods cannot be called with named arguments, cannot be composed and are hard to type for static analysers.

Readonly result objects carry those values now:

| New method | Returns |
| ---------- | ------- |
| `JWSVerifier::verify()` | `VerificationResult` — `isVerified()`, `getSignatureIndex()`, `getKey()` |
| `JWEDecrypter::decrypt()` | `DecryptionResult` — `isDecrypted()`, `getJwe()`, `getRecipientIndex()`, `getKey()` |
| `JWSLoader::loadAndVerify()` | `LoadingResult` — `getJws()`, `getSignatureIndex()`, `getKey()` |
| `JWELoader::loadAndDecrypt()` | `LoadingResult` — `getJwe()`, `getRecipientIndex()`, `getKey()` |
| `NestedTokenLoader::loadAndVerify()` | `LoadingResult` |
| `JWSSerializerManager::unserializeToken()` | `UnserializationResult` — `getJws()`, `getSerializerName()` |
| `JWESerializerManager::unserializeToken()` | `UnserializationResult` — `getJwe()`, `getSerializerName()` |

**Before:**

```php
$jws = $jwsLoader->loadAndVerifyWithKeySet($token, $jwkset, $signature);
// $signature has been written into by the loader
```

**After:**

```php
$result = $jwsLoader->loadAndVerify($token, $jwkset);

$jws       = $result->getJws();
$signature = $result->getSignatureIndex();
$key       = $result->getKey();       // The key that verified the signature
```

The new methods accept a `JWK` **or** a `JWKSet`, so the `*WithKey()`/`*WithKeySet()` pairs collapse into one method. The callable that observes the keys discarded along the way — introduced in 4.2 and read with `func_get_arg()` until now — is a declared argument:

```php
$result = $jwsVerifier->verify($jws, $jwkset, 0, null, static function (Throwable $e): void {
    // Called for each key that could not verify the signature
});
```

`JWEDecrypter::decrypt()` also fixes a long standing oddity: it leaves the JWE it is given untouched and carries the decrypted one in the result, instead of writing the payload into the object by reference.

```php
$result = $jweDecrypter->decrypt($jwe, $jwkset, 0);

if ($result->isDecrypted()) {
    $payload = $result->getJwe()->getPayload(); // $jwe itself is unchanged
}
```

!!! info

    The algorithm interfaces and `TokenTypeSupport` cannot change without breaking every third-party implementation, so 4.3 only documents the signature they will have in 5.0 and ships the objects they will return. See [Announced For 5.0](#announced-for-50).

### The builders are really immutable

The builders advertised an immutable `with*()` API they did not honour: they accumulated state on the receiver, which is why `create()` existed — not as a named constructor, but as a reset.

Every accumulation method now clones first and never touches the receiver, and every check spanning several calls is performed by `build()`, **so the order of the calls no longer matters**:

* `JWSBuilder::addSignature()` no longer pins the payload encoding on the receiver. The `b64` consistency checks are read from the signatures by `build()`.
* `JWEBuilder::addRecipient()` no longer resolves the key and content encryption algorithms. They are read from the complete header of each recipient by `build()`, so a recipient can be added *before* the shared headers carrying its `alg` and `enc`.
* The [disjoint header requirement](from-v4.1-to-v4.2.md#stricter-header-validation-on-decryption) of RFC 7516 is verified for the three headers by `build()`, whatever the order in which they were set.

As a consequence, a builder can be reused safely:

```php
$base = (new JWSBuilder($algorithmManager))->withPayload($payload);

$first  = $base->addSignature($key1, ['alg' => 'HS256'])->build();
$second = $base->addSignature($key2, ['alg' => 'RS256'])->build(); // $base is untouched
```

`create()` is deprecated: there is no state to reset any more. Remove the call. Until 5.0, it returns a new, empty builder and leaves the one it is called on untouched: if your code ignores what it returns, read [Behaviour changes](#behaviour-changes).

### Immutable managers

A manager expresses a policy — *these algorithms and no others* — so a consumer must not be able to widen it. `AlgorithmManager::add()` mutated a service that is usually shared; it is deprecated in favour of `with()`, which returns a new manager and leaves the current one untouched:

```php
$restricted = $algorithmManager->with(new ES256(), new ES384());
```

The state of the checker and serializer managers is now `readonly`, and both serializer managers are `readonly` classes.

### Typed accessors on the JWK

Reading a parameter meant writing the same three steps every time: `has()`, then `get()`, then a type assertion, because `get()` returns an undeclared `mixed` and throws when the parameter is absent.

```php
$jwk->kty();             // string — always present
$jwk->alg();             // ?string — null when the key is not restricted to an algorithm
$jwk->use();             // ?string — null when the key is not restricted to a usage
$jwk->getString('kid');  // string — asserts the parameter is a string
$jwk->find('kid');       // mixed — null instead of throwing when absent
```

`JWK` and `JWKSet` announce that they become `final readonly` in 5.0. `JWKSet::sortKeys()` was public only because the comparison was passed to `usort()` as a callable; it is a closure now and calling the method is deprecated. Conversely, `getIterator()` lost the `@internal` annotation that wrongly told users not to iterate over a key set.

### The key factory is an injectable service

`JWKFactory` was a bag of sixteen static methods, half of which reach for OpenSSL, for sodium or for the filesystem. Application code generating or loading keys could not be unit tested without any of them, and the factory could not be decorated to audit, cache or delegate the generation to a hardware backed implementation.

The behaviour now lives in instance methods behind `JWKFactoryInterface`. The names lose the `create` prefix, which was only there because the methods were static:

| Static method (deprecated) | Instance method |
| -------------------------- | --------------- |
| `JWKFactory::createRSAKey()` | `rsa()` |
| `JWKFactory::createECKey()` | `ec()` |
| `JWKFactory::createOctKey()` | `oct()` |
| `JWKFactory::createOKPKey()` | `okp()` |
| `JWKFactory::createNoneKey()` | `none()` |
| `JWKFactory::createFromJsonObject()` | `fromJsonObject()` |
| `JWKFactory::createFromValues()` | `fromValues()` |
| `JWKFactory::createFromSecret()` | `fromSecret()` |
| `JWKFactory::createFromCertificateFile()` | `fromCertificateFile()` |
| `JWKFactory::createFromCertificate()` | `fromCertificate()` |
| `JWKFactory::createFromX509Resource()` | `fromX509Resource()` |
| `JWKFactory::createFromX5C()` | `fromX5C()` |
| `JWKFactory::createFromKeyFile()` | `fromKeyFile()` |
| `JWKFactory::createFromKey()` | `fromKey()` |
| `JWKFactory::createFromPKCS12CertificateFile()` | `fromPKCS12CertificateFile()` |
| `JWKFactory::createFromKeySet()` | `fromKeySet()` |

```php
<?php

use Jose\Component\KeyManagement\JWKFactoryInterface;

final readonly class MyKeyProvider
{
    public function __construct(
        private JWKFactoryInterface $jwkFactory,
    ) {
    }

    public function newSigningKey(): JWK
    {
        return $this->jwkFactory->ec('P-256', ['use' => 'sig', 'alg' => 'ES256']);
    }
}
```

The bundle registers `JWKFactory` — it already did — and now aliases it with its interface, so `JWKFactoryInterface $factory` is autowired. The static methods keep working and delegate to a default instance.

### A JOSE exception hierarchy

Every exception thrown by the library implements the `Jose\Component\Core\Exception\JoseException` marker interface, so a single catch block handles any failure reported by the framework:

```php
<?php

use Jose\Component\Core\Exception\JoseException;

try {
    $result = $jwsLoader->loadAndVerify($token, $jwkset);
} catch (JoseException $throwable) {
    // The cause, when there is one, is available through $throwable->getPrevious()
}
```

**Each new exception extends the SPL class that was thrown at that place before**, hence the existing catch blocks keep matching. The Checker exceptions join the hierarchy as well.

Two failures gained a precise type: both loaders report a token that cannot be loaded with `InvalidTokenException`, where the JWS loader used to throw a bare `Exception` and the JWE loader a `RuntimeException`.

A token beyond the bounds of the JSON decoder, more than 4,096 JSON values or more than 511 levels, is rejected with a `JsonBoundExceededException`. It extends `InvalidArgumentException`, which the JSON serializers threw for such a token. See [Rejections for a bound](../advanced-topics/serialization.md#rejections-for-a-bound).

### Sealed internal mutators

`JWS::addSignature()` and `JWE::withPayload()` were public only because the objects are not built in one go — the first is what the builder and the serializers use to append a signature, the second is how the decrypter injects the plaintext it just authenticated. Both were reachable by anybody holding a token, so a JWS returned by a loader could gain a signature that was never verified, and the payload of a decrypted JWE could be replaced by an arbitrary value.

Calling either method from outside the library now raises a deprecation notice; they are removed in 5.0, where the objects are built by their constructor. A custom JWS serializer is a supported extension point and keeps working.

### Sealed value objects

`JWK`, `JWKSet`, `JWS`, `JWE` and `Signature` were documented as becoming `final readonly` in 5.0, but only in prose: unlike the services, they carried no `@final` annotation and raised nothing when they were extended. They now do both.

The notice is not the one the services raise. A value object has no interface to decorate in place of the inheritance: it carries no behaviour to change, and the state a subclass adds to it cannot survive the constructor becoming the only way to populate it.

**What to do:** build the object with its constructor, and keep the state your subclass adds in the object of yours that uses it.

```php
// Instead of extending JWK to carry your own metadata:
final readonly class ManagedKey
{
    public function __construct(
        public JWK $key,
        public DateTimeImmutable $rotatedAt,
    ) {
    }
}
```

### `ES256K` leaves the experimental package

`ES256K` (ECDSA over secp256k1, [RFC 8812](https://www.rfc-editor.org/rfc/rfc8812.html)) has been a standard algorithm since 2020 but was shipped in the experimental package. It is now `Jose\Component\Signature\Algorithm\ES256K`, registered by the bundle under the same `ES256K` alias, with an `ES256KKeyAnalyzer` for its keys.

```diff
-use Jose\Experimental\Signature\ES256K;
+use Jose\Component\Signature\Algorithm\ES256K;
```

The experimental class is kept until 5.0 as a deprecated subclass of the new one — instantiating it raises a deprecation — and the bundle keeps its service, deprecated too, for the applications that inject it. Nothing changes for the tokens.

### ML-DSA, the first post-quantum signature

[RFC 9964](https://www.rfc-editor.org/rfc/rfc9964.html) registers ML-DSA (FIPS 204) for JOSE: the `ML-DSA-44`, `ML-DSA-65` and `ML-DSA-87` algorithms and the `AKP` key type. The library ships all three, over keys whose `priv` is the 32-byte seed of FIPS 204 — the only private key representation the RFC allows — and whose `alg` is required.

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\KeyManagement\JWKFactory;
use Jose\Component\Signature\Algorithm\MLDSA65;

$key = (new JWKFactory())->mldsa('ML-DSA-65');          // A fresh key
$key = (new JWKFactory())->mldsa('ML-DSA-65', ['priv' => $seed]); // Rebuilt from its stored seed
$algorithmManager = new AlgorithmManager([new MLDSA65()]);
```

`JWK::thumbprint()` computes the RFC 9964 section 6 thumbprint of an AKP key (over `alg`, `kty` and `pub`), `toPublic()` strips `priv`, the key loader reads the RFC 9881 PEM forms and the certificates holding such a key, a `MLDSAKeyAnalyzer` checks the key structure, and `key:generate:mldsa` / `keyset:generate:mldsa` generate keys.

The computation is OpenSSL's and needs **PHP 8.4 and an OpenSSL 3.5 runtime**, checked at runtime: `MLDSA44::isSupported()` tells, the constructors throw a `MissingDependencyException` naming the missing piece, and the Symfony Bundle registers the algorithms only when they can run. See the [signature algorithms](../the-components/signed-tokens-jws/signature-algorithms.md#the-ml-dsa-44-ml-dsa-65-and-ml-dsa-87-algorithms) page.

### `Ed25519`, `Ed448` and `X448`

[RFC 9864](https://www.rfc-editor.org/rfc/rfc9864.html) registers the fully-specified `Ed25519` and `Ed448` signature algorithms and deprecates the polymorphic `EdDSA`: the name of the algorithm alone must say which curve is in use. The library ships both, and `EdDSA` is deprecated. The keys are unchanged — an `OKP` key with `crv: Ed25519` or `crv: Ed448` — only the `alg` value differs.

```php
<?php

use Jose\Component\Core\AlgorithmManager;
use Jose\Component\Signature\Algorithm\Ed25519;
use Jose\Component\Signature\Algorithm\Ed448;

$algorithmManager = new AlgorithmManager([new Ed25519(), new Ed448()]);
```

The same release closes the RFC 8037 gap on the `448` curves: `Ed448` keys sign and verify, `X448` keys work with every `ECDH-ES*` and `ECDH-SS*` algorithm, `JWKFactory::okp()` and `key:generate:okp` generate both, and a new `OKPKeyAnalyzer` checks the structure of the `OKP` keys.

Two platform notes:

* `Ed448` and `X448` run on OpenSSL and need **PHP 8.4 or later**: before that version PHP cannot ask OpenSSL for the digest-less signature or the raw key material of these curves. `Ed448::isSupported()` tells whether the platform can run the algorithm, its constructor throws a `MissingDependencyException` when it cannot, and the Symfony Bundle registers it only when it can run.
* `Ed25519` and `X25519` still use the `sodium` extension when it is loaded. On PHP 8.4 they now fall back to OpenSSL when it is not, so `sodium` is no longer required there.

**Migrating from `EdDSA`** — the algorithm keeps working, the tokens already in circulation still verify, and signing with it raises a deprecation notice. Register `Ed25519` next to `EdDSA` on the verifiers, switch the issuer to `alg: Ed25519` with the same key, then drop `EdDSA` once no old token is left. A key carrying `alg: EdDSA` is refused by the `Ed25519` algorithm (and the reverse), so update the `alg` of the keys with the issuer, or leave it out during the migration. The key analyzer reports the keys that still carry `alg: EdDSA`. See the [signature algorithms](../the-components/signed-tokens-jws/signature-algorithms.md#the-ed25519-and-ed448-algorithms) page.

### JWK thumbprint URI

[RFC 9278](https://www.rfc-editor.org/rfc/rfc9278.html) names a key by its RFC 7638 thumbprint: `urn:ietf:params:oauth:jwk-thumbprint:sha-256:NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs`. It is the key-based `sub` or `kid` of OAuth DPoP, SIOP v2, OpenID for Verifiable Credentials and OpenID Federation, and every implementer had to build it by hand.

```php
<?php

use Jose\Component\Core\JwkThumbprintUri;

$jwk->thumbprintUri();                        // The URI, "sha-256" by default
$jwk->thumbprintUri('sha-512');               // The hash function is given by its IANA name

JwkThumbprintUri::parse($sub)->matches($jwk); // Verifier side: does this key match the URI?
$jwkset->selectKeyByThumbprintUri($sub);      // Or find the key in a key set; null if none matches
```

The console command `key:thumbprint` gains a `--uri` option. See the [Key](../the-components/key-jwk-and-key-set-jwkset/key-management.md#thumbprint-uri) page.

### Explicit typing with the `typ` header

[RFC 8725 section 3.11](https://www.rfc-editor.org/rfc/rfc8725.html#section-3.11) recommends that a verifier accepts only the token profile it expects — `at+jwt`, `dpop+jwt`, `secevent+jwt`, `logout+jwt`… — so that a token issued for one purpose cannot be replayed for another one. The library had checkers for `alg`, `exp`, `iss` or `aud`, but none for `typ`.

The new `Jose\Component\Checker\TypeChecker` closes the gap. It only reads the protected header and compares the media types as RFC 7515 defines them: case-insensitively, with an optional `application/` prefix.

```php
<?php

use Jose\Component\Checker\TypeChecker;

$headerCheckerManagerFactory->add('typ', new TypeChecker(['at+jwt']));
$headerCheckerManager = $headerCheckerManagerFactory->create(['alg', 'typ']);
$headerCheckerManager->check($jws, 0, ['alg', 'typ']); // "typ" is mandatory
```

In the Symfony Bundle, a header checker manager declares the accepted types directly:

```yaml
jose:
    checkers:
        headers:
            access_token:
                headers: ['alg']
                typ: ['at+jwt']
```

The `ConfigurationHelper::addHeaderChecker()` helper accepts the same list as an additional argument after the tags. See the [Header Checker](../the-components/header-checker.md#explicit-typing-with-the-typ-header) page.

### Selective Disclosure for JWTs (SD-JWT)

[RFC 9901](https://www.rfc-editor.org/rfc/rfc9901.html) lets an Issuer sign a JWT whose claims the Holder discloses one by one to each Verifier, optionally bound to the key of the Holder. It is the credential format of SD-JWT VC, of the EU Digital Identity Wallet and of OpenID for Verifiable Credentials.

The new `web-token/jwt-selective-disclosure` package (`composer require web-token/jwt-selective-disclosure`) implements the three roles of the RFC on top of the JWS services of the library, in the `Jose\SelectiveDisclosure` namespace:

```php
<?php

use Jose\SelectiveDisclosure\Disclosable;

// Issuer
$sdJwt = $issuer->issue(['iss' => $iss, 'given_name' => new Disclosable('John'), 'cnf' => ['jwk' => $holderPublicKey->all()]], $issuerPrivateKey, ['alg' => 'ES256', 'typ' => 'example+sd-jwt']);

// Holder
$presentation = $holder->present($sdJwt->select(['given_name']), $holderPrivateKey, ['alg' => 'ES256'], $audience, $nonce);

// Verifier
$claims = $verifier->verifyWithKeyBinding($presentation->toString(), $issuerKeySet, $audience, $nonce)->getClaims();
```

Both formats of the RFC are supported: the compact format and the JWS JSON serialization of section 8, issued by `issueJson()`.

The Symfony Bundle creates the services from a `jose.selective_disclosure` configuration once the package is installed. See the [Selective Disclosure](../advanced-topics/selective-disclosure.md) page.

### JKUFactory and X5UFactory stand on their own

`UrlKeySetFactory` is announced for removal in 5.0, yet `JKUFactory` and `X5UFactory` — the documented way to load a `jku` or a `x5u` key set, and not deprecated themselves — extended it.

The fetching code moved to an internal trait the two factories use. They **still extend `UrlKeySetFactory` in 4.3**, so the code that type-hints that class keeps receiving them, but they never run its code: neither of them emits a deprecation, nor does a class of yours that extends them. `UrlKeySetFactory` now says what is deprecated — itself, as a public extension point — and extending it directly raises a notice. In 5.0, the class is removed and the two factories no longer extend it: type-hint `JKUFactory` or `X5UFactory` instead.

`enabledCache()`, deprecated by annotation since 4.1, raises the notice now and states its replacement: an HTTP client that caches the responses, which honours the cache directives of the endpoint where the fixed lifetime of a cache pool ignores them.

### A redirect policy for JKUFactory and X5UFactory

`JKUFactory` and `X5UFactory` followed the redirects of the endpoint as their HTTP client does: up to 20, to any host, the last response giving the key set. Their constructor takes a redirect policy as a second argument: `false` refuses the redirects, `true` follows them. Without it, a key set fetched through a redirect raises a deprecation notice, and 5.0 refuses the redirects by default. With the Symfony bundle, set the `jose.jku_factory.follow_redirects` option.

```php
$jkuFactory = new JKUFactory($httpClient, false);
```

See [Redirects](../the-components/key-jwk-and-key-set-jwkset/key-set-management.md#redirects).

### A maximum number of signatures and recipients

Since 4.2.6, `JWSLoader` and `JWELoader` take the maximum number of signatures or recipients of a token as a fourth argument. In 4.3, the loader factories take it as the fourth argument of `create()`, and the bundle as the `max_signatures` and `max_recipients` options of a loader.

Without a maximum, loading a token with more than 10 signatures or recipients is deprecated: 5.0 sets 10 by default. Only the JSON General serialization carries more than one. See [JWS loading](../the-components/signed-tokens-jws/jws-loading.md#maximum-number-of-signatures) and [JWE loading](../the-components/encrypted-tokens-jwe/jwe-loading.md#maximum-number-of-recipients).

### The place of `cty` in a nested token

A JWE carries a nested token when its `cty` header parameter is `JWT`. In the JSON serializations, the loader also found it in the unprotected headers, which no authentication tag covers. Loading such a token is deprecated, and 5.0 refuses it by default. A third argument of `NestedTokenLoader` sets the policy now: `false` refuses these tokens, `true` loads them without notice. `NestedTokenLoaderFactory::create()` takes the value as its seventh argument, and the bundle as the `allow_unprotected_content_type` option of a loader. Tokens whose `cty` is in the protected header, every compact token among them, are not concerned.

See [The cty header parameter](../advanced-topics/nested-tokens.md#the-cty-header-parameter).

## Announced for 5.0

Some interfaces of the library are implemented by third-party code, so they cannot change without breaking it. 4.3 is the last release able to give notice, so it documents the signature they will have in 5.0 and **ships the objects they will return**, ready to be used.

None of these interfaces changes in 4.3: nothing to do today, unless you maintain an implementation.

### Encryption algorithms

The key management algorithms write the header parameters they need to add to the token — `epk`, `iv`, `tag`, `p2s`… — into an array of the caller. In 5.0 they return a `WrappedKey` carrying both the key and those parameters:

| Method | 5.0 signature |
| ------ | ------------- |
| `KeyEncryption::encryptKey()` | `encryptKey(JWK $key, string $cek, array $completeHeader): WrappedKey` |
| `KeyWrapping::wrapKey()` | `wrapKey(JWK $key, string $cek, array $completeHeader): WrappedKey` |
| `KeyAgreement::getAgreementKey()` | `getAgreementKey(int $encryptionKeyLength, string $algorithm, JWK $recipientKey, ?JWK $senderKey, array $completeHeader): WrappedKey` |
| `KeyAgreementWithKeyWrapping::wrapAgreementKey()` | `wrapAgreementKey(JWK $recipientKey, ?JWK $senderKey, string $cek, int $encryptionKeyLength, array $completeHeader): WrappedKey` |

```php
use Jose\Component\Encryption\Algorithm\KeyEncryption\WrappedKey;

$wrapped = new WrappedKey($encryptedCek, ['iv' => $iv, 'tag' => $tag]);

$wrapped->getKey();
$wrapped->getAdditionalHeader();
```

The content encryption algorithms do the same with their authentication tag. `ContentEncryptionAlgorithm::encryptContent()` returns an `EncryptedContent` in 5.0 and loses its `?string &$tag` parameter:

```php
use Jose\Component\Encryption\Algorithm\EncryptedContent;

$encrypted = new EncryptedContent($ciphertext, $tag);

$encrypted->getCiphertext();
$encrypted->getTag();       // null when the algorithm computes none
```

`decryptKey()` and `unwrapKey()` gain their fourth argument, [the expected CEK size](../advanced-topics/custom-algorithm.md#the-expected-cek-size) introduced in 4.2, as a declared and required parameter in the same release.

### Token type supports

`TokenTypeSupport::retrieveTokenHeaders()` is the last public interface of the library built entirely on output parameters: it writes the two headers into variables of the caller and returns `void`. In 5.0 it returns a `TokenHeaders`:

```php
// 4.3
public function retrieveTokenHeaders(JWT $jwt, int $index, array &$protectedHeader, array &$unprotectedHeader): void;

// 5.0
public function retrieveTokenHeaders(JWT $jwt, int $index): TokenHeaders;
```

```php
use Jose\Component\Checker\TokenHeaders;

$headers = new TokenHeaders($protectedHeader, $unprotectedHeader);

$headers->getProtectedHeader();
$headers->getUnprotectedHeader();
```

A support given a token it does not handle returns an object carrying two empty headers, which is what it does today by leaving the two output parameters untouched.

## Behaviour changes

Most of these changes need nothing from your code. Three of them may:

* you exchange AES-CBC-HMAC tokens with an AAD: upgrade the applications that decrypt them first;
* you catch the errors of a builder around a single call;
* you call `create()` on a builder without using what it returns.

The points worth knowing:

* **`JWEDecrypter::decrypt()` does not modify the JWE it receives.** The deprecated `decryptUsingKey()`/`decryptUsingKeySet()` still write the payload into the object passed by reference, so both behaviours coexist until 5.0.
* **The builders no longer depend on the order of the calls.** Sequences that used to fail — adding a recipient before the shared protected header carrying its `alg`, or reusing a shared builder service after a `b64` build — now succeed. In return, some errors are reported later. They keep their messages, and their classes are the ones thrown before or subclasses of them: a `try` block around the whole sequence still catches them, but a `try` block around the method that used to throw does not.
    * `JWEBuilder` checks the headers, the algorithms and the keys of the recipients in `build()`. `withSharedProtectedHeader()`, `withSharedHeader()` and `addRecipient()` checked them before and throw nothing any more.
    * `JWSBuilder::addSignature()` still checks the signature it adds. The consistency of `b64` among the signatures, and with a payload set by `withEncodedPayload()`, is checked by `build()`; `addSignature()` and `withEncodedPayload()` checked it before.
* **`create()` no longer empties the builder it is called on.** It returns a new, empty builder and leaves the receiver untouched. A call that ignores the result, such as `$builder->create();` before reusing `$builder`, used to drop the payload, the headers and the signatures or recipients of `$builder`. Now they stay: a signature or a recipient added next comes on top of the old ones. Remove the call and start from the builder service again, which nothing modifies any more, or use what `create()` returns.
* **The loaders return the interfaces of their services.** `getJwsVerifier()` returns a `JWSVerifierInterface`, `getJweDecrypter()` a `JWEDecrypterInterface` and `getHeaderCheckerManager()` a `?HeaderCheckerManagerInterface`. This applies to the `JWSLoader` and `JWELoader` of the library and to those of the bundle. They return the object the loader was built with, so nothing changes when your code runs. Static analysers only know the interface, though, so call `verify()` or `decrypt()` and type-hint the interfaces. Otherwise:
    * a call to the deprecated `verifyWithKeySet()`, `decryptUsingKey()` or `decryptUsingKeySet()` on the returned object is reported as a call to an undefined method;
    * passing the object where a `JWSVerifier`, a `JWEDecrypter` or a `HeaderCheckerManager` is expected is reported as a type error.
* **The key analyzer reports `alg: EdDSA`.** `AlgorithmAnalyzer` adds a `medium` message to a key whose `alg` is `EdDSA`: `The algorithm "EdDSA" is deprecated. Use the fully-specified "Ed25519" algorithm instead.`, or `"Ed448"` for a key on that curve. The bundle registers this analyzer, so the `key:analyze` and `keyset:analyze` commands and the profiler of the bundle report it as well. A check that rejects keys with any message, or with a `medium` one, now flags these keys. See [Migrating from `EdDSA`](#ed25519-ed448-and-x448).
* **AES-CBC-HMAC tokens with an AAD follow RFC 7518.** The authentication tag of `A128CBC-HS256`, `A192CBC-HS384` and `A256CBC-HS512` covers the length of the whole authenticated data, where earlier versions counted the protected header only. Other implementations accept the tokens of 4.3, and 4.3 accepts theirs. The tokens issued by earlier versions still decrypt, with a deprecation notice, but earlier versions cannot decrypt the tokens issued by 4.3. Only the JSON serializations with an `aad` member are concerned. See [AES-CBC-HMAC tokens with an AAD](../advanced-topics/encrypted-tokens/additional-authentication-data-aad.md#aes-cbc-hmac-tokens-with-an-aad).
* **The key agreement algorithms accept `deriveKey` and `deriveBits`.** A key whose `key_ops` lists either operation can be used by the `ECDH-*` algorithms to build and to decrypt, as WebCrypto exports such keys with either. See [Key operations](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#key-operations-key_ops).
* **The RSA public key operation is computed by OpenSSL.** Encrypting with `RSA-OAEP`, `RSA-OAEP-256` and `RSA1_5`, and verifying `PS*` signatures, no longer depend on the GMP or BCMath extension for their speed. Decryption still does: GMP remains recommended.
* **The size of a key wrapped with AES Key Wrap is checked before it is unwrapped.** No token changes outcome; a wrongly sized one fails with `Invalid encrypted key size`.
* **The serializers name the bound a token goes beyond.** A token of more than 4,096 JSON values or more than 511 levels was rejected with the message of invalid JSON. The message now names the bound, and the serializer managers chain that rejection, whichever serializer they tried last. The managers and the loaders keep their own messages. See [Rejections for a bound](../advanced-topics/serialization.md#rejections-for-a-bound).

An unrelated misconfiguration is now reported early: passing an algorithm that is neither a key encryption nor a content encryption algorithm to `JWEBuilder` or `JWEDecrypter` is deprecated, where it used to turn into a much later *algorithm not supported* error.

## Dangerous algorithms move to their own packages

The `none` signature algorithm and the `RSA1_5` key encryption algorithm are standard but dangerous: the first disables signature verification altogether, the second uses a padding vulnerable to the Bleichenbacher adaptive chosen-ciphertext attack. Both were shipped in the main library and were as easy to enable as any other algorithm.

They now live in two dedicated packages, so that using them is an explicit and auditable decision:

| Algorithm | Package | Class |
| --------- | ------- | ----- |
| `none` | `web-token/jwt-unsecured` | `Jose\Unsecured\Signature\None` |
| `RSA1_5` | `web-token/jwt-rsa15` | `Jose\Rsa15\KeyEncryption\RSA15` |

They are deliberately **not** moved to `web-token/jwt-experimental`: they are perfectly standard, and an application asking for `Blake2b` should not get `none` in the bargain.

The classes of the library are kept until 5.0 as empty deprecated subclasses of the new ones, so the migration is a `composer require` and a change of `use` statement:

```bash
composer require web-token/jwt-unsecured   # only if you use "none"
composer require web-token/jwt-rsa15       # only if you use "RSA1_5"
```

```diff
-use Jose\Component\Signature\Algorithm\None;
+use Jose\Unsecured\Signature\None;

-use Jose\Component\Encryption\Algorithm\KeyEncryption\RSA15;
+use Jose\Rsa15\KeyEncryption\RSA15;
```

The Symfony Bundle registers the classes of the new packages, so applications that never enable those algorithms are not flooded with a deprecation they cannot act on. The configuration aliases are unchanged: `none` and `RSA1_5` still name them. The services of the former classes stay until 5.0 for the applications that inject them, deprecated and no longer tagged, like the experimental `ES256K` one. Injecting one raises the deprecation of the service, then the one of the class.

!!! warning

    If you are still using one of these two algorithms, take the opportunity to reconsider. See [Security Recommendations](../introduction/security-recommendations.md#avoid-weak-algorithms).

## Deprecation summary

Everything below still works in 4.3 and is removed in 5.0.

### Services

| Deprecated | Replacement |
| ---------- | ----------- |
| `JWSBuilder::create()`, `JWEBuilder::create()` | Remove the call — the builders are immutable |
| Extending `JWSBuilder`, `JWSVerifier`, `JWSLoader`, `JWEBuilder`, `JWEDecrypter`, `JWELoader`, `NestedTokenBuilder`, `NestedTokenLoader`, `ClaimCheckerManager`, `HeaderCheckerManager` | Implement the matching interface, or decorate the service |
| `JWSVerifier::verifyWithKeySet()` | `verify()` |
| `JWEDecrypter::decryptUsingKey()`, `decryptUsingKeySet()` | `decrypt()` |
| `JWSLoader::loadAndVerifyWithKey()`, `loadAndVerifyWithKeySet()` | `loadAndVerify()` |
| `JWELoader::loadAndDecryptWithKey()`, `loadAndDecryptWithKeySet()` | `loadAndDecrypt()` |
| The `$signature` argument of `NestedTokenLoader::load()` | `loadAndVerify()` |
| The `$name` argument of `JWSSerializerManager::unserialize()` and `JWESerializerManager::unserialize()` | `unserializeToken()` |

`JWSVerifier::verifyWithKey()` is **not** deprecated: it takes a single key and returns a boolean, with no output parameter.

### Managers and factories

| Deprecated | Replacement |
| ---------- | ----------- |
| `AlgorithmManager::add()` | `with()` |
| `JWSSerializerManagerFactory::names()`, `JWESerializerManagerFactory::names()` | `aliases()` |
| Passing a non-encryption algorithm to `JWEBuilder` or `JWEDecrypter` | Remove it from the algorithm manager |
| Two different checkers of the same claim or header parameter in one `ClaimCheckerManager` or `HeaderCheckerManager` | One checker per [claim](../the-components/claim-checker.md#one-checker-per-claim) or [header parameter](../the-components/header-checker.md#one-checker-per-header-parameter): combine the rules in a single checker |
| `JWSLoaderFactory` and `JWELoaderFactory`, of the library or of the bundle, without a header checker manager factory | A `HeaderCheckerManagerFactory` with the `JWSTokenSupport` or `JWETokenSupport` token type support; with the bundle, its factory services. See [JWS loading](../the-components/signed-tokens-jws/jws-loading.md#without-a-header-checker-manager-factory) |
| Loading a token with more than 10 signatures or recipients without a maximum | A maximum: fourth argument of the loader or of `create()`, `max_signatures` or `max_recipients` with the bundle |

### Keys

| Deprecated | Replacement |
| ---------- | ----------- |
| The sixteen static `JWKFactory::createXxx()` methods | Inject `JWKFactoryInterface` — see [the table above](#the-key-factory-is-an-injectable-service) |
| `JWKSet::sortKeys()` | None — it is an implementation detail of `selectKey()` |
| `UrlKeySetFactory::enabledCache()` | An HTTP client that caches the responses |
| Extending or type-hinting `UrlKeySetFactory` | `JKUFactory`, `X5UFactory`, or your own implementation. The two factories still extend it in 4.3, but no longer in 5.0 |
| `JKUFactory` and `X5UFactory` fetching a key set through a redirect without a redirect policy | The final URL, or `false` (refuse) or `true` (follow) as the second argument; `follow_redirects` with the bundle |
| A `dir` key longer than the content encryption key | A key of exactly that size: its first bytes still decrypt the tokens already issued. See [Direct encryption](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#direct-encryption-dir) |
| An AES key wrapping key longer than its algorithm key size | A key of exactly 128, 192 or 256 bits: its first bytes still decrypt the tokens already issued. See [AES key wrapping keys](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#aes-key-wrapping-keys) |
| A `dir` key whose `key_ops` lacks `encrypt` (to build) or `decrypt` (to decrypt) | Add both operations, or remove `key_ops`. See [Key operations](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#key-operations-key_ops) |

### Tokens

| Deprecated | Replacement |
| ---------- | ----------- |
| `JWS::addSignature()` called from outside the library | `JWSBuilder` |
| `JWE::withPayload()` called from outside the library | `JWEDecrypter` |
| Extending `JWK`, `JWKSet`, `JWS`, `JWE` or `Signature` | Build the object with its constructor and keep your own state beside it |
| `new Signature($sig, $decodedProtectedHeader, null, ...)` | Pass the encoded protected header — the decoded one is silently discarded without it, and this throws in 5.0 |
| A `dir` JWE with neither a protected header nor an AAD | Put `alg` and `enc` in the shared protected header |
| An `RSA-OAEP` or `RSA-OAEP-256` encrypted key shorter than the modulus | Nothing on the receiving side: conforming senders produce an encrypted key as long as the modulus. See [RSA keys](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#rsa-keys) |
| An AES-CBC-HMAC token with an AAD whose tag was computed by a version before 4.3 | Encrypt it again with 4.3, once the applications that decrypt it are upgraded |
| A nested token whose `cty` is outside the protected header of the JWE, without a policy | `cty` in the protected header on the issuing side; `false` or `true` as the third argument of `NestedTokenLoader`, or the `allow_unprotected_content_type` option of the bundle |

### Algorithms

| Deprecated | Replacement |
| ---------- | ----------- |
| `Jose\Component\Signature\Algorithm\None` | `Jose\Unsecured\Signature\None` (`web-token/jwt-unsecured`) |
| `Jose\Component\Encryption\Algorithm\KeyEncryption\RSA15` | `Jose\Rsa15\KeyEncryption\RSA15` (`web-token/jwt-rsa15`) |
| The hardcoded `RSA1_5` CEK size table | Read the [expected CEK size](../advanced-topics/custom-algorithm.md#the-expected-cek-size) argument |
| `Jose\Component\Signature\Algorithm\EdDSA` (deprecated by RFC 9864; its removal is a 5.0 candidate) | `Ed25519` — same key, `alg: Ed25519` |
| `Jose\Experimental\Signature\ES256K` | `Jose\Component\Signature\Algorithm\ES256K` |

### Symfony bundle

| Deprecated | Replacement |
| ---------- | ----------- |
| The `Jose\Bundle\JoseFramework\Services` classes that extend a service of the library: `JWSBuilder`, `JWSVerifier`, `JWSLoader`, `JWEBuilder`, `JWEDecrypter`, `JWELoader`, `NestedTokenBuilder`, `NestedTokenLoader`, `ClaimCheckerManager` and `HeaderCheckerManager` | Type-hint the interfaces of the library. The bundle still creates these classes in 4.3. In 5.0, it creates the `EventDispatching*` decorators under the same service ids instead, with no configuration change. The decorators are available now for the services you build yourself |
| The `Jose\Component\Signature\Algorithm\None`, `Jose\Component\Encryption\Algorithm\KeyEncryption\RSA15` and `Jose\Experimental\Signature\ES256K` services | The services of the new classes, registered under the same `none`, `RSA1_5` and `ES256K` aliases |
| Two services tagged with the same alias (`jose.algorithm`, `jose.checker.header`, `jose.checker.claim`) | One alias per service; to replace a service of the bundle, redefine its id or decorate it. See [One service per alias](../the-symfony-bundle/header-and-claim-checker-management.md#one-service-per-alias) |

The event dispatching verifier and decrypter of the bundle used to drop the callable the loaders pass to observe the discarded keys, so the reason of a failure was lost as soon as the bundle services were used. They forward it now, as the new decorators do.
