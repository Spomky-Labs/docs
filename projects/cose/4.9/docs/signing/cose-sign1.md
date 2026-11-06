---
description: 'Creating and verifying a message with a single signer.'
---

# COSE_Sign1

The `COSE_Sign1` structure is used when a message has a single signer.

## Creating a COSE_Sign1 message

```php
use CBOR\ByteStringObject;
use CBOR\ListObject;
use CBOR\MapItem;
use CBOR\MapObject;
use CBOR\NegativeIntegerObject;
use CBOR\Tag\CoseSign1Tag;
use CBOR\UnsignedIntegerObject;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Key\Ec2Key;
use Cose\Signature\Signature1;
use Cose\Structure\HeaderMapHelper;

$algorithm = ES256::create();
$key = Ec2Key::create($yourPrivateCoseKey);

// Define headers
$protectedHeader = MapObject::create([
    MapItem::create(
        UnsignedIntegerObject::create(1),                  // alg
        NegativeIntegerObject::create(ES256::identifier()) // ES256 (-7)
    ),
]);
$unprotectedHeader = MapObject::create([
    MapItem::create(
        UnsignedIntegerObject::create(4),                  // kid
        ByteStringObject::create('my-key-id')
    ),
]);
$payload = ByteStringObject::create('Message to sign');

// The signature covers the Sig_structure, never the payload on its own. Encode the protected bucket once, so the
// bytes that are signed are the bytes the message carries. HeaderMapHelper applies RFC 9052 §3 on the way out: an
// empty map becomes h'' rather than h'a0', and the labels are checked (§1.5, §9).
$protectedHeaderAsBytes = HeaderMapHelper::encodeProtected($protectedHeader);
$toBeSigned = Signature1::create($protectedHeaderAsBytes, $payload);
$signature = ByteStringObject::create($algorithm->sign((string) $toBeSigned, $key));

// Assemble the message around those exact bytes
$coseSign1 = CoseSign1Tag::create(ListObject::create([
    $protectedHeaderAsBytes,
    $unprotectedHeader,
    $payload,
    $signature,
]));

// Encode to CBOR
$encoded = (string) $coseSign1;
```

!!! note

    `CoseSign1Tag::createFromComponents($protectedHeader, $unprotectedHeader, $payload, $signature)` takes the protected
    header as a **map** and encodes it itself, which is shorter but re-encodes what you already signed. Use it when the
    signature is computed after the message, and `create()`, as above, when the bytes have to travel verbatim.
    [`examples/01-sign1.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/01-sign1.php) is the whole round trip, key generation included, and runs as it
    stands.

## Decoding and verifying a COSE_Sign1 message

```php
use CBOR\Decoder;
use CBOR\ListObject;
use CBOR\OtherObject\NullObject;
use CBOR\StringStream;
use CBOR\Tag\CoseSign1Tag;
use Cose\Algorithm\Signature\ECDSA\ES256;
use Cose\Key\Ec2Key;
use Cose\Signature\Signature1;
use Cose\Structure\CoseHeaders;

// The key of the signer you trust, and the algorithm you expect it to be used with.
$key = Ec2Key::create($theCoseKeyYouPinned);
$algorithm = ES256::create();
// The protected header labels this application knows how to process (1 = alg, 2 = crit).
$understoodLabels = [1, 2];

// cbor-php 3.4.0 registers the six COSE tags in the default decoder: tag 18 resolves on its own.
$coseSign1 = Decoder::create()->decode(new StringStream($encodedData));
if (! $coseSign1 instanceof CoseSign1Tag) {
    throw new RuntimeException('Not a COSE_Sign1 message');
}

// cbor-php carries the header buckets; this library reads them the way RFC 9052 defines them.
$headers = CoseHeaders::fromMessage($coseSign1);

// RFC 9052 §3.1: bind the signature to the algorithm the protected header declares.
// The label is matched by type as well as by value, so the text string "1", a different label under §1.5,
// never answers a lookup for the integer label 1.
$alg = $headers->getProtectedHeaderParameter(1);
if ($alg === null || (int) $alg->normalize() !== $algorithm::identifier()) {
    throw new RuntimeException('Unexpected or missing "alg" in the protected header');
}

// RFC 9052 §3.1: every parameter listed in "crit" must be processed, or the message must be rejected.
$crit = $headers->getProtectedHeaderParameter(2);
if ($crit !== null) {
    if (! $crit instanceof ListObject) {
        throw new RuntimeException('"crit" is not an array');
    }
    foreach ($crit as $label) {
        if (! in_array((int) $label->normalize(), $understoodLabels, true)) {
            throw new RuntimeException('Unsupported critical header parameter');
        }
    }
}

// RFC 9052 §4.2: a nil payload is detached and the application supplies the content itself.
$payload = $coseSign1->getPayload();
if ($payload instanceof NullObject) {
    throw new RuntimeException('The payload is detached; supply it from the application');
}

// Verify the Sig_structure the signature covers
$sigStructure = Signature1::create($coseSign1->getProtectedHeader(), $payload);
$isValid = $algorithm->verify((string) $sigStructure, $key, $coseSign1->getSignature()->getValue());
```

`tests/Signature/DocumentedVerifierTest.php` runs exactly this code, against a genuine ES256 message and against
messages crafted to exercise each check.

The other accessors of the message and of its headers:

```php
$protectedHeader = $coseSign1->getProtectedHeader();     // ByteStringObject: what the signature covers verbatim
$unprotectedHeader = $coseSign1->getUnprotectedHeader(); // MapObject
$signature = $coseSign1->getSignature();                 // ByteStringObject

$protectedHeaderMap = $headers->getProtectedHeaderAsMap(); // MapObject, checked
$kid = $headers->getHeaderParameter(4);                    // ?CBORObject, protected bucket first
```
