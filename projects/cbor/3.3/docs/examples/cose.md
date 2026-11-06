---
description: Reading a COSE message, and where its boundaries are
---

# COSE

COSE, [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052), is what JOSE is for JSON: signed,
MACed and encrypted messages, written in CBOR. A `COSE_Sign1` — one signer, the common case — is an array
of four items, usually wrapped in [tag 18](../tags/registering.md#cose-and-cwt).

```php
use CBOR\Decoder;
use CBOR\ListObject;
use CBOR\StringStream;
use CBOR\Tag;

$decoded = Decoder::create()->decode(StringStream::create($binaryData));

// Tag 18 is not registered in this version: a tagged message arrives as a GenericTag.
$message = $decoded instanceof Tag ? $decoded->getValue() : $decoded;

if (! $message instanceof ListObject || count($message) !== 4) {
    throw new RuntimeException('A COSE_Sign1 is an array of four items');
}

$protected = $message->get(0)->getValue();   // bytes: a CBOR map, encoded
$unprotected = $message->get(1);             // a map, in the clear
$payload = $message->get(2)->getValue();     // bytes, or null
$signature = $message->get(3)->getValue();   // bytes
```

The protected header is a byte string that holds an encoded CBOR map, and the payload is a byte string
too. That is deliberate: the signature covers those exact bytes. Decode the protected header to read it,
never to rewrite it.

```php
$headers = Decoder::create()->decode(StringStream::create($protected));
$alg = $headers->get(1)->normalize(); // the algorithm label
```

Verifying the signature means rebuilding the `Sig_structure` of the specification and handing it to a
signature algorithm, which is outside what this library does.
[web-auth/cose-lib](https://github.com/web-auth/cose-lib) does it, on top of this one: use it rather than
assembling the pieces yourself.
