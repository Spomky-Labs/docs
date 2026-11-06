---
description: 'The six COSE message types of RFC 9052, each a CBOR tag, and where their classes come from.'
---

# Messages, structures and headers

What RFC 9052 defines above the CBOR: the six message types, the structures a signature, a MAC or an
encryption is computed over, and the rules that decide what a header says.

- [Cryptographic structures](cryptographic-structures.md) — what a signature, a MAC or an encryption
  actually covers
- [Reading headers](reading-headers.md) — the RFC 9052 rules a raw map lookup does not apply
- [Common header parameters](common-header-parameters.md) — every label the library reads, with its
  accessor
- [Detached content](detached-content.md) — a payload that travels outside the message
- [External additional authenticated data](external-additional-authenticated-data.md) — data bound to the
  message without travelling in it

## COSE tags

COSE defines six message types, each a CBOR tag. The classes come from
[spomky-labs/cbor-php](https://github.com/Spomky-Labs/cbor-php) 3.4.0 or later; the `Cose\...Tag` classes
this library used to ship are deprecated, see [Upgrading](../migration/upgrading.md).

| Tag | Value | Class (cbor-php 3.4.0+) | Description |
|-----|-------|--------------------------|-------------|
| COSE_Encrypt0 | 16 | `CBOR\Tag\CoseEncrypt0Tag` | Single recipient encrypted message |
| COSE_Mac0 | 17 | `CBOR\Tag\CoseMac0Tag` | MAC without recipients |
| COSE_Sign1 | 18 | `CBOR\Tag\CoseSign1Tag` | Single signature structure |
| CWT | 61 | `CBOR\Tag\CwtTag` | CBOR Web Token ([RFC 8392](https://datatracker.ietf.org/doc/html/rfc8392)) |
| COSE_Encrypt | 96 | `CBOR\Tag\CoseEncryptTag` | Multiple recipients encrypted message |
| COSE_Mac | 97 | `CBOR\Tag\CoseMacTag` | MAC with recipients |
| COSE_Sign | 98 | `CBOR\Tag\CoseSignTag` | Multiple signatures structure |

All seven are registered in the default decoder, so `Decoder::create()` resolves them without any
`TagManager` configuration:

```php
use CBOR\Decoder;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;

$message = Decoder::create()->decode(new StringStream($encodedData));
if (! $message instanceof CoseSign1Tag) {
    throw new RuntimeException('Not a COSE_Sign1 message');
}
```
