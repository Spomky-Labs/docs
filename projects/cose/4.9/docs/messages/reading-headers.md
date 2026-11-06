---
description: 'CoseHeaders applies the RFC 9052 header rules that a raw CBOR map lookup cannot.'
---

# Reading headers

cbor-php carries the two header buckets; RFC 9052 decides what they mean. `Cose\Structure\CoseHeaders`
applies the second part to any COSE message:

```php
use Cose\Structure\CoseHeaders;

$headers = CoseHeaders::fromMessage($coseSign1);   // any CBOR\Tag\Cose*Tag

$headers->getProtectedHeaderParameter(1);          // ?CBORObject, protected bucket only
$headers->getUnprotectedHeaderParameter(4);        // ?CBORObject, unprotected bucket only
$headers->getHeaderParameter(1);                   // ?CBORObject, protected first, then unprotected
$headers->getProtectedHeaderAsMap();               // MapObject, decoded and checked
```

## What it enforces

Why the raw `MapObject` accessors are not enough:

- **A label is an integer *or* a text string**
  ([§1.5](https://datatracker.ietf.org/doc/html/rfc9052#section-1.5)), and the two are different labels.
  cbor-php normalizes the integer `1`, the text string `"1"` and the byte string `h'31'` to the same map
  offset, so `$map->has(1)` answers `true` for all three. `getProtectedHeaderParameter(1)` matches the
  type as well, and only the integer `1` is the algorithm parameter.
- **A byte-string key is not a label at all** and makes the header malformed.
- **The zero-length protected header is accepted**
  ([§3](https://datatracker.ietf.org/doc/html/rfc9052#section-3): "Recipients MUST accept both a
  zero-length byte string and a zero-length map encoded in a byte string"), and **trailing bytes inside
  the protected bucket are not**: the CDDL `bstr .cbor header_map` holds exactly one item.
- **The protected bucket wins a combined lookup**, because that is the value the signature or the MAC
  commits to.

For a per-signer or per-recipient bucket, `CoseSignature` and `CoseRecipient` expose the same lookups; see
[COSE_Sign](../signing/cose-sign.md) and [COSE_Encrypt](../encryption/cose-encrypt.md); for a header map
you assembled yourself, use `CoseHeaders::of($protectedBytes, $unprotectedMap)`.
`Cose\Structure\HeaderMapHelper` holds the same rules as static functions, including `encodeProtected()`
and `assertTagNumber()`.

## The nesting bound

The protected header is decoded with a decoder bounded to
`CoseHeaders::DEFAULT_PROTECTED_HEADER_MAX_DEPTH` (32) levels of nesting. Pass your own `Decoder` when a
header carries custom CBOR tags, or a different `$maxDepth` when 32 is not the right bound:

```php
use CBOR\Decoder;
use CBOR\OtherObject\OtherObjectManager;
use CBOR\Tag\TagManager;

$customDecoder = Decoder::create(
    TagManager::create()->add(MyCustomTag::class),
    OtherObjectManager::create(),
    32
);
$headers = CoseHeaders::fromMessage($coseSign1, $customDecoder);
```

## The parameters with a rule of their own

Some header parameters come with a rule that a raw lookup cannot apply, and have a typed accessor: `typ`
and `CWT Claims` are described with [CBOR Web Tokens](../header-parameters/cwt.md#typ-and-cwt-claims), the
X.509 parameters in [X.509 header parameters](../header-parameters/x509.md), the hash envelope parameters
in [Hash envelope](../header-parameters/hash-envelope.md), the countersignature labels in
[Countersignatures](../signing/countersignatures.md), the `receipts`, `vds` and `vdp` parameters in
[Receipts](../header-parameters/receipts.md), and the ECDH and HKDF parameters of a `COSE_recipient` in
[Key management](../key-management/README.md).
