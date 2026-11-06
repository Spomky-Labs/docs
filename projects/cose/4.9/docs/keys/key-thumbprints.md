---
description: 'The COSE Key Thumbprint of RFC 9679, and the kid it makes.'
---

# Key thumbprints

`Cose\Key\Thumbprint` computes the COSE Key Thumbprint of [RFC 9679](https://www.rfc-editor.org/rfc/rfc9679.html),
the COSE counterpart of the JWK Thumbprint of RFC 7638: a digest of the key that depends on the key and on nothing
else. It is what a producer can use as a `kid`, what the `ckt` member of a CWT `cnf` claim carries
([§5.6](https://www.rfc-editor.org/rfc/rfc9679#section-5.6)), and what the URI of
[§5.7](https://www.rfc-editor.org/rfc/rfc9679#section-5.7) names.

The computation follows [§3](https://www.rfc-editor.org/rfc/rfc9679#section-3): a `COSE_Key` holding only the
required parameters of the key type ([§4](https://www.rfc-editor.org/rfc/rfc9679#section-4)) is built from scratch,
encoded in the deterministic encoding of [RFC 8949 §4.2.1](https://www.rfc-editor.org/rfc/rfc8949#section-4.2.1),
shortest-form integers and lengths, map keys sorted in the bytewise order of their encodings, and hashed. The map
the key was decoded from is never re-encoded, so:

- `kid`, `alg`, `key_ops`, `Base IV` and the private parts do not affect the result;
- neither does the order of the members, nor whether `kty` and `crv` were given as integers, as numeric strings or
  as names; the canonical form always carries the integers of the IANA registries;
- an EC2 key carrying `y` as a sign bit and the same key carrying the coordinate have the same thumbprint, computed
  over the uncompressed point as [§4.2](https://www.rfc-editor.org/rfc/rfc9679#section-4.2) requires;
- a private key has the thumbprint of its public half, an OKP private key without `x` included.

| Key type | Required parameters | Reference |
|----------|---------------------|-----------|
| OKP | `kty` (1), `crv` (-1), `x` (-2) | [RFC 9679 §4.1](https://www.rfc-editor.org/rfc/rfc9679#section-4.1) |
| EC2 | `kty` (1), `crv` (-1), `x` (-2), `y` (-3) | [RFC 9679 §4.2](https://www.rfc-editor.org/rfc/rfc9679#section-4.2) |
| RSA | `kty` (1), `n` (-1), `e` (-2) | [RFC 9679 §4.3](https://www.rfc-editor.org/rfc/rfc9679#section-4.3) |
| Symmetric | `kty` (1), `k` (-1) | [RFC 9679 §4.4](https://www.rfc-editor.org/rfc/rfc9679#section-4.4) |
| AKP | `kty` (1), `alg` (3), `pub` (-1) | [RFC 9964 §6](https://www.rfc-editor.org/rfc/rfc9964#section-6) |

The AKP row is the one place `alg` is part of the digest: RFC 9679 §4.6 defers the required parameters of any other
key type to its own specification, and RFC 9964 §6 lists `alg` among them, because the AKP type alone does not say
what the key is: the same `pub` bytes under another algorithm would be another key. An AKP key without `alg` has no
thumbprint and `Thumbprint::of()` refuses it. The `kid` of every COSE example of RFC 9964 Appendix A.2 is that
thumbprint. A generic `Cose\Key\Key` of a type this library has no class for, HSS-LMS (5), has no thumbprint
here either.

```php
use Cose\Algorithm\Hash\SHA256;
use Cose\Algorithm\Hash\SHA384;
use Cose\Key\Key;
use Cose\Key\Thumbprint;

$key = Key::createFromData($decodedCoseKey);

$thumbprint = Thumbprint::of($key);              // with SHA-256, which §3 requires every implementation to support
$thumbprint->value();                            // the 32 raw bytes: a kid, or the value of a "ckt"
$thumbprint->toUri();                            // 'urn:ietf:params:oauth:ckt:sha-256:SWvYr63zB-WwjGSwQhv53AFSijRKQ72oj63RZp2iU-w'
$thumbprint->hash();                             // the SHA256 instance it was computed with
Thumbprint::canonicalForm($key);                 // the CBOR bytes the digest is computed over, for a cross-check

// Another hash of RFC 9054: the parameter is typed Hash, so SHA1 and SHA256_64 (Filter Only) are refused
Thumbprint::of($key, SHA384::create())->toUri(); // 'urn:ietf:params:oauth:ckt:sha-384:…'

// Verifying the "ckt" confirmation method of a CWT (RFC 9679 §5.6, RFC 8747): cnf (8) => { ckt (5) => bstr }
$confirmed = Thumbprint::of($presentedKey)->equals($claims[8][5]);
```

`equals()` compares with `hash_equals()`. The hash segment of the URI must be a name of the IANA
[Named Information Hash Algorithm Registry](https://www.iana.org/assignments/named-information/named-information.xhtml)
([§5.7](https://www.rfc-editor.org/rfc/rfc9679#section-5.7)), and that registry names `sha-256`, `sha-384` and
`sha-512` only among the hashes of RFC 9054: `toUri()` throws an `InvalidArgumentException` for a thumbprint made with
SHA-512/256, SHAKE128 or SHAKE256, whose `value()` is nonetheless computed.

**Symmetric keys.** The thumbprint of a symmetric key is a digest of the secret, and therefore a public identifier of
a secret value. [RFC 9679 §7](https://www.rfc-editor.org/rfc/rfc9679#section-7): "Thumbprints MUST NOT be used with
passwords or other low-entropy secrets"; a randomly selected key of at least 128 bits is safe to name this way, and
"if a developer is unable to determine whether all symmetric keys used in an application have sufficient entropy,
then thumbprints of symmetric keys MUST NOT be used".

[`examples/12-key-thumbprint.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/12-key-thumbprint.php) reproduces the worked example of
[RFC 9679 §6](https://www.rfc-editor.org/rfc/rfc9679#section-6) byte for byte.
