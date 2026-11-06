---
description: Reading a COSE message with the tags the library ships
---

# COSE

COSE, [RFC 9052](https://datatracker.ietf.org/doc/html/rfc9052), is what JOSE is for JSON: signed, MACed
and encrypted messages, written in CBOR. Its six structures and the CWT tag that wraps them
[are built in](../tags/registry-tags.md#cose-and-cwt) and registered by default, so a tagged message
decodes to a class that knows its own shape.

```php
use CBOR\Decoder;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;

$object = Decoder::create()->decode(StringStream::create($binaryData));

if ($object instanceof CoseSign1Tag) {
    $protectedHeader = $object->getProtectedHeaderAsMap(); // the signed header, decoded
    $payload = $object->getPayload();                      // ByteStringObject, or NullObject when detached
    $signature = $object->getSignature();

    $algorithm = $protectedHeader->normalize()[1] ?? null;
}
```

The protected header travels as a byte string holding an encoded CBOR map, and the payload as a byte
string too. That is deliberate: the signature covers those exact bytes. `getProtectedHeaderAsMap()`
decodes a copy for you to read — it does not replace the bytes that were signed, and you should not
re-encode them yourself.

A payload that is `null` is a detached one: the content travelled out of band, and only the signature came
with the structure. Check for it before you use the payload.

```php
use CBOR\OtherObject\NullObject;

if ($payload instanceof NullObject) {
    // the content is elsewhere; the verifier has to be given it
}
```

## A token

A CWT is tag 61 around one of those structures, or around a bare claims set:

```php
use CBOR\Tag\CwtTag;

if ($object instanceof CwtTag) {
    $inner = $object->getValue(); // a COSE structure, or the claims as a MapObject
}
```

## What this library does not do

Verifying a signature or a MAC means rebuilding the `Sig_structure` of the specification, finding the key,
and running the algorithm the header names. None of that is CBOR, and none of it is here.
[web-auth/cose-lib](https://github.com/web-auth/cose-lib) does it, on top of this library, with the
algorithm registry of RFC 9053: use it rather than assembling the pieces yourself.
