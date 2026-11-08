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

$jkuFactory = new JKUFactory($httpClient);
$jwkset = $jkuFactory->loadFromUrl('https://login.microsoftonline.com/common/discovery/keys');

$x5uFactory = new X5UFactory($httpClient);
$jwkset = $x5uFactory->loadFromUrl(
    'https://www.googleapis.com/oauth2/v1/certs',
    ['X-Api-Key' => $apiKey] // Optional headers of the request
);
```

!!! danger

    Only fetch URLs your application trusts, such as one written in its configuration. The `jku` and `x5u` header parameters of a token are chosen by its sender: never fetch them unless they are in an exact list of trusted URLs.

### Redirects

The factories send their request with the redirect policy of the HTTP client: Symfony's clients follow up to 20 redirects by default, to any host, and the body of the last response becomes the key set. To refuse redirects, give the factory a client whose `max_redirects` option is 0: a redirect then makes `loadFromUrl()` throw.

```php
$jkuFactory = new JKUFactory(HttpClient::create(['max_redirects' => 0]));
```

### Certificates of a `x5u` document

Each entry of a `x5u` document is a certificate, PEM encoded or as the base64 body of its PEM form. Since 4.2.7, an entry that starts with `file://` is wrapped between PEM markers like any other base64 entry: OpenSSL never receives it as a path, so the document cannot make the application read a local file, and such an entry fails to load.

### Cache

`enabledCache()` stores the fetched documents in a PSR-6 cache pool. It is deprecated since 4.1: give the factory an HTTP client that caches the responses instead, such as Symfony's `CachingHttpClient`.

Since 4.2.7, the cache key covers the URL **and the headers** of the request: two calls for the same URL with other headers, for instance another tenant or other credentials, fetch their own document. Before, the second call got the document fetched with the first headers until the entry expired. The entries stored by an earlier version are not read any more, so the first call after the upgrade fetches the document again. A request whose headers cannot be serialized, such as an anonymous `Stringable` object, bypasses the cache: it is sent on every call and never stored.

!!! info

    A caching HTTP client must tell those requests apart too. Symfony's `CachingHttpClient` separates the responses of one URL by the request headers that their `Vary` header names: an endpoint that picks the key set from a custom header must list that header in `Vary`.
