---
description: 'A payload or a ciphertext that travels outside the message, as a nil in its place.'
---

# Detached content

[RFC 9052 §4.1](https://datatracker.ietf.org/doc/html/rfc9052#section-4.1) lets the payload, or the
ciphertext of an encrypted message, travel outside the message, as a `nil` in its place:

```php
use CBOR\ByteStringObject;
use CBOR\OtherObject\NullObject;
use CBOR\Tag\CoseSign1Tag;
use Cose\Signature\Signature1;

// Sending
$coseSign1 = CoseSign1Tag::createFromComponents(
    $protectedHeader,
    $unprotectedHeader,
    NullObject::create(),
    $signature
);

// Receiving: the application supplies the content it transported separately
$payload = $coseSign1->getPayload();
if ($payload instanceof NullObject) {
    $payload = ByteStringObject::create($contentYouTransportedSeparately);
}

$toBeSigned = Signature1::create($coseSign1->getProtectedHeader(), $payload);
```

[`examples/07-detached-and-external-aad.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/07-detached-and-external-aad.php)
shows this and [external_aad](external-additional-authenticated-data.md) together.
