---
description: 'A single recipient that already holds the content encryption key.'
---

# COSE_Encrypt0

```php
use CBOR\ByteStringObject;
use CBOR\ListObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\Tag\CoseEncrypt0Tag;
use CBOR\UnsignedIntegerObject;
use Cose\Algorithm\ContentEncryption\A128GCM;
use Cose\Encryption\Encrypt0Structure;
use Cose\Encryption\InitializationVector;
use Cose\Key\SymmetricKey;
use Cose\Structure\HeaderMapHelper;

$algorithm = A128GCM::create();
$key = SymmetricKey::create([
    SymmetricKey::TYPE => SymmetricKey::TYPE_OCT,
    SymmetricKey::DATA_K => $sharedSecret, // 16 bytes for A128GCM
]);
// The key and nonce pair MUST be unique for every message (RFC 9053 §4.1.1)
$nonce = random_bytes($algorithm->nonceLength());

// Encode the protected bucket once: the bytes the AEAD authenticates are the bytes the message carries
$protectedHeader = HeaderMapHelper::encodeProtected(MapObject::create([
    MapItem::create(UnsignedIntegerObject::create(1), UnsignedIntegerObject::create($algorithm::identifier())),
]));
$unprotectedHeader = MapObject::create([
    MapItem::create(UnsignedIntegerObject::create(InitializationVector::IV), ByteStringObject::create($nonce)),
]);

// ["Encrypt0", protected, external_aad] is the AAD; the result is the ciphertext followed by the tag
$ciphertext = Encrypt0Structure::create($protectedHeader)->encrypt($algorithm, $key, $plaintext, $nonce);

$coseEncrypt0 = CoseEncrypt0Tag::create(ListObject::create([
    $protectedHeader,
    $unprotectedHeader,
    ByteStringObject::create($ciphertext),
]));
```

Decrypting rebuilds the structure from the bytes the message carries, and resolves the nonce from its headers:

```php
use Cose\Structure\CoseHeaders;

$headers = CoseHeaders::fromMessage($coseEncrypt0);
$nonce = InitializationVector::resolve($headers, $algorithm->nonceLength(), $key);
$plaintext = Encrypt0Structure::create($coseEncrypt0->getProtectedHeader())
    ->decrypt($algorithm, $key, $coseEncrypt0->getCiphertext()->getValue(), $nonce);
```

`decrypt()` throws an `InvalidArgumentException` when the content does not authenticate. A wrong key, a wrong nonce,
a rewritten protected header, an external AAD the sender did not use, a tag that was tampered with, replaced or
truncated: the primitive cannot tell them apart, and the library reports all of them with the same message
(`Aead::DECRYPTION_FAILED`).

[`examples/04-encrypt0.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/04-encrypt0.php) runs the whole of it, `IV` and `Partial IV` included.
