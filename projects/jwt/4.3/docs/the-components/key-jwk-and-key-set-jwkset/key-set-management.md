# Key set (JWKSet)

You can create a JWKSet object using three static methods:

* `new JWKSet(array $keys)`: creates a JWKSet using a list of JWK objects.
* `JWKSet::createFromJson(string $json)`: creates a JWKSet using a JSON object.
* `JWKSet::createFromKeyData(array $values)`: creates a JWKSet using a decoded JSON object.

Below are all methods available for a JWKSet object. The variable `$jwkset` is a valid JWKSet object.

!!! warning

    Please note a JWKSet object is an immutable object. When you add keys, you get a new JWKSet object.

```php
<?php
// Returns all keys
$jwkset->all();

// Check if the key set has the key with the key ID 'KEY ID'.
$jwkset->has('KEY ID');

// Retrieve the key with the key ID 'KEY ID'.
$jwkset->get('KEY ID');

// Counts the keys in the key set.
$jwkset->count(); // The method count($jwkset) has the same behaviour.

// Adds a key to the key set.
// /!\ As the JWKSet object is immutable, this method will create a new key set. The previous key set is unchanged.
$newJwkset = $jwkset->with($jwk);

// Removes a key from the key set.
// /!\ As the JWKSet object is immutable, this method will create a new key set. The previous key set is unchanged.
$newJwkset = $jwkset->without('KEY ID');

// Selects a key according to the requirements.
// The first argument is the key usage ("sig" or "enc")
// The second argument is the algorithm to be used (optional)
// The third argument is an associative array of constraints (optional)
$key = $jwkset->selectKey('sig', $algorithm, ['kid' => 'KEY ID']);

// You can iterate on a key set
foreach($jwkset as $kid => $jwk) {
    // Action with the key done here
}

// The JWKSet object can be serialized into JSON
json_encode($jwkset);
```

## Lookup by thumbprint URI

A key set can be searched with a [JWK Thumbprint URI](key-management.md#thumbprint-uri) (RFC 9278). The thumbprint of every key is recomputed with the hash function named by the URI, so the lookup does not depend on the `kid` of the keys. Given the `sub` of a DPoP proof or of a SIOP `id_token`, it finds the key the token is bound to; `null` is returned when no key matches.

```php
<?php
$key = $jwkset->selectKeyByThumbprintUri('urn:ietf:params:oauth:jwk-thumbprint:sha-256:NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs');
```

A malformed URI or an unsupported hash function throws; a key whose thumbprint cannot be computed is skipped, as `selectKey()` does with malformed keys.

!!! info

    Available since 4.3.

## Duplicate key IDs

[RFC 7517 section 4.5](https://datatracker.ietf.org/doc/html/rfc7517#section-4.5) explicitly allows a key set to hold several keys sharing the same `kid`, typically an RSA key and an EC key that the application considers as equivalent alternatives.

Such keys are all kept:

```php
<?php

use Jose\Component\Core\JWKSet;

// Both keys carry "kid" => "key-1"
$jwkset = new JWKSet([$rsaKey, $ecKey]);

count($jwkset);        // 2
$jwkset->get('key-1'); // The first key registered with that ID
```

* `get()` and `has()` look the key ID up and return the first key carrying it.
* `without('key-1')` removes **every** key carrying that ID.

!!! info

    When several keys share a `kid`, prefer `selectKey()` over `get()`: it also takes the key usage and the algorithm into account, which is precisely what tells those keys apart.

!!! warning

    Before 4.2, the keys were indexed by `kid` and the last key registered with a given ID silently replaced the previous one. See the [migration guide](../../migration/from-v4.1-to-v4.2.md#duplicate-key-ids-in-a-key-set).

## Distant key sets

`JKUFactory` and `X5UFactory` fetch a key set from a URL with a [Symfony HTTP client](https://symfony.com/doc/current/http_client.html). `JKUFactory` reads a JWKSet document, `X5UFactory` a JSON object of X.509 certificates. The second argument of `loadFromUrl()` holds the headers of the request.

```php
<?php

use Jose\Component\KeyManagement\JKUFactory;
use Jose\Component\KeyManagement\X5UFactory;
use Symfony\Component\HttpClient\HttpClient;

$httpClient = HttpClient::create();

$jkuFactory = new JKUFactory($httpClient, false); // false: redirects are refused, see below
$jwkset = $jkuFactory->loadFromUrl('https://login.microsoftonline.com/common/discovery/keys');

$x5uFactory = new X5UFactory($httpClient, false);
$jwkset = $x5uFactory->loadFromUrl(
    'https://www.googleapis.com/oauth2/v1/certs',
    ['X-Api-Key' => $apiKey] // Optional headers of the request
);
```

!!! danger

    Only fetch URLs your application trusts, such as one written in its configuration. The `jku` and `x5u` header parameters of a token are chosen by its sender: never fetch them unless they are in an exact list of trusted URLs, and fetch them with redirects refused.

### Redirects

Symfony's HTTP clients follow up to 20 redirects by default, to any host, and the body of the last response becomes the key set. Since 4.3, the second argument of the constructor of `JKUFactory` and `X5UFactory` sets their redirect policy:

| Second argument | Redirects |
|---|---|
| `false` | Refused. The request carries `max_redirects: 0`, so the request a redirect points to is never sent. A redirect answer, or a response the client reached through a redirect anyway, makes `loadFromUrl()` throw `Unable to get the key set: redirects are refused.`, with the status code as the code of the exception. |
| `true` | Followed by the HTTP client, as before. |
| absent or `null` | Followed by the HTTP client, but a key set fetched through a redirect triggers a deprecation. |

Any other value makes the constructor throw an `InvalidArgumentException`. With the bundle, set the [`follow_redirects`](../../the-symfony-bundle/key-and-key-set-management/key-set-management-jwkset.md#redirects) option.

!!! warning

    Fetching a key set through a redirect without a redirect policy is deprecated since 4.3, and 5.0 refuses redirects by default. Use the URL the redirect leads to, or pass `false` to refuse redirects, or `true` to keep following them. The argument is read with `func_num_args()`/`func_get_arg(1)` until 5.0 declares it.

### Certificates of a `x5u` document

Each entry of a `x5u` document is a certificate, PEM encoded or as the base64 body of its PEM form. Since 4.2.7, an entry that starts with `file://` is wrapped between PEM markers like any other base64 entry: OpenSSL never receives it as a path, so the document cannot make the application read a local file, and such an entry fails to load.

### Cache

`enabledCache()` stores the fetched documents in a PSR-6 cache pool. It is deprecated since 4.1, and triggers a deprecation notice since 4.3: give the factory an HTTP client that caches the responses instead, such as Symfony's `CachingHttpClient`.

Since 4.2.7, the cache key covers the URL **and the headers** of the request: two calls for the same URL with other headers, for instance another tenant or other credentials, fetch their own document. Before, the second call got the document fetched with the first headers until the entry expired. The entries stored by an earlier version are not read any more, so the first call after the upgrade fetches the document again. A request whose headers cannot be serialized, such as an anonymous `Stringable` object, bypasses the cache: it is sent on every call and never stored. A factory that refuses redirects does not read the entries of a factory that follows them, even in a shared pool.

!!! info

    A caching HTTP client must tell those requests apart too. Symfony's `CachingHttpClient` separates the responses of one URL by the request headers that their `Vary` header names: an endpoint that picks the key set from a custom header must list that header in `Vary`.

## Sealed helpers

Two methods carried an `@internal` annotation that did not match what they are:

* `sortKeys()` was public only because the comparison was passed to `usort()` as a callable. It is a closure now, nothing in the library calls the method any more, and calling it is deprecated since 4.3.
* `getIterator()` carried the same annotation although it is the `IteratorAggregate` contract, which wrongly told users not to iterate over a key set. Iterating is supported, as the example above shows.

!!! warning

    `JWKSet` becomes `final readonly` in 5.0, and extending it raises a deprecation notice since 4.3. Like the [key](key-management.md#typed-accessors), it is a value object with no interface to decorate: move to composition now — build the key set with its constructor and keep your own state in the object that uses it.
