---
description: 'A MAC without recipients: the symmetric key is shared out of band.'
---

# COSE_Mac0

```php
use CBOR\ByteStringObject;
use CBOR\ListObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\Tag\CoseMac0Tag;
use CBOR\UnsignedIntegerObject;
use Cose\Algorithm\Mac\HS256;
use Cose\Key\SymmetricKey;
use Cose\Mac\Mac0Structure;
use Cose\Structure\HeaderMapHelper;

$algorithm = HS256::create();
$key = SymmetricKey::create([
    SymmetricKey::TYPE => SymmetricKey::TYPE_OCT,
    SymmetricKey::DATA_K => $sharedSecret, // 32 bytes for HS256
]);

// Encode the protected bucket once: the bytes the tag covers are the bytes the message carries
$protectedHeader = HeaderMapHelper::encodeProtected(MapObject::create([
    MapItem::create(UnsignedIntegerObject::create(1), UnsignedIntegerObject::create($algorithm::identifier())),
]));
$payload = ByteStringObject::create('Data to authenticate');

// The tag covers the MAC_structure ["MAC0", protected, external_aad, payload], never the payload alone
$toBeMaced = Mac0Structure::create($protectedHeader, $payload);
$tag = ByteStringObject::create($algorithm->hash((string) $toBeMaced, $key));

$coseMac0 = CoseMac0Tag::create(ListObject::create([
    $protectedHeader,
    MapObject::create(),
    $payload,
    $tag,
]));
```

Verifying rebuilds the structure from the bytes the message carries:

```php
$toBeMaced = Mac0Structure::create($coseMac0->getProtectedHeader(), $coseMac0->getPayload());
$isValid = $algorithm->verify((string) $toBeMaced, $key, $coseMac0->getTag()->getValue()); // compared with hash_equals()
```

[`examples/03-mac0.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/03-mac0.php) runs the whole of it, with HMAC and then with AES-CBC-MAC.
