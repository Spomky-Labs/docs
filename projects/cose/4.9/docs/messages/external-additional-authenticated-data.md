---
description: 'Data the application supplies on both sides, bound to the signature, the MAC or the encryption without travelling in the message.'
---

# External additional authenticated data

Every structure takes the optional `external_aad` of
[RFC 9052 §4.4](https://datatracker.ietf.org/doc/html/rfc9052#section-4.4) as its last argument: data the
application supplies on both sides and that never travels in the message, yet is bound to the signature,
the MAC or the encryption. It defaults to the zero-length byte string the RFC prescribes:

```php
use CBOR\ByteStringObject;
use Cose\Signature\Signature1;

$toBeSigned = Signature1::create(
    $coseSign1->getProtectedHeader(),
    $payload,
    ByteStringObject::create($applicationSuppliedData),
);
```

[`examples/07-detached-and-external-aad.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/07-detached-and-external-aad.php)
shows this and [detached content](detached-content.md) together.
