---
description: Encoding and decoding CBOR in PHP, after RFC 8949
---

# CBOR PHP

CBOR, the Concise Binary Object Representation of
[RFC 8949](https://datatracker.ietf.org/doc/html/rfc8949), is a binary data format built on a data model
close to the one JSON describes, with a few things JSON lacks: byte strings, a tag mechanism that carries
meaning, and an encoding small enough for a constrained device.

CBOR PHP encodes and decodes it. Every major type of the specification is implemented, definite and
indefinite length alike, with the tags of the IANA registry that applications actually meet and a way to
write the ones they do not.

```php
use CBOR\Decoder;
use CBOR\MapObject;
use CBOR\StringStream;
use CBOR\TextStringObject;
use CBOR\UnsignedIntegerObject;

$map = MapObject::create()
    ->add(TextStringObject::create('name'), TextStringObject::create('John Doe'))
    ->add(TextStringObject::create('age'), UnsignedIntegerObject::create(30));

$encoded = (string) $map;

$decoded = Decoder::create()->decode(StringStream::create($encoded));

$data = $decoded->normalize();
// ['name' => 'John Doe', 'age' => '30']
```

## What CBOR buys you

-   **It is compact.** Smaller than JSON for most data, and no base64 detour for bytes.
-   **It is quick.** A binary encoding, read and written without a text parser.
-   **It carries meaning.** A tag says what a value is: an instant, a big integer, a URI, a signed
    message.
-   **It is specified.** One specification, one registry of tags held by IANA.
-   **It holds everything.** Every major type, binary data included.

## Where you meet it

-   **WebAuthn and FIDO2**: the attestation objects and the authenticator data of a credential.
-   **COSE**: signing and encryption, the CBOR counterpart of JOSE.
-   **CWT**: CBOR Web Tokens, where JWT would use JSON.
-   **CoAP**: the payloads of the protocol constrained devices speak.
-   **The Internet of things**: sensor readings, on a link that counts its bytes.
-   **APIs**: a binary answer where JSON costs too much.

## Where to go next

-   [Installation](installation.md) — the package, the versions of PHP, the extensions worth having.
-   [The data model](concepts/the-data-model.md) — the major types and the classes that stand for them.
-   [Encoding](guide/encoding.md) and [decoding](guide/decoding.md) — the two halves of the library.
-   [Tags](tags/overview.md) — what a tag is, the ones that ship, and writing your own.
-   [The Symfony bundle](bundle.md) — the decoder as a service, in a Symfony application.
-   [Quick reference](quick-reference.md) — the whole library on one page.
