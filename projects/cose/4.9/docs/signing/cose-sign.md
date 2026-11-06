---
description: 'Multiple signatures from different signers, and the Signature structure each one covers.'
---

# COSE_Sign

The `COSE_Sign` structure supports multiple signatures from different signers.

```php
use CBOR\ByteStringObject;
use CBOR\ListObject;
use CBOR\MapObject;
use CBOR\Tag\CoseSignTag;
use Cose\Signature\CoseSignature;

$protectedHeader = MapObject::create();
$unprotectedHeader = MapObject::create();
$payload = ByteStringObject::create('Document to be signed');

// Create signature structures for each signer
$signatures = ListObject::create([
    ListObject::create([
        ByteStringObject::create(''), // signature protected header
        MapObject::create([/* signer 1 unprotected header */]),
        ByteStringObject::create($signature1Bytes)
    ]),
    ListObject::create([
        ByteStringObject::create(''),
        MapObject::create([/* signer 2 unprotected header */]),
        ByteStringObject::create($signature2Bytes)
    ]),
]);

$coseSign = CoseSignTag::createFromComponents(
    $protectedHeader,
    $unprotectedHeader,
    $payload,
    $signatures
);

// Reading them back as checked views rather than raw lists
foreach (CoseSignature::all($coseSign->getSignatures()) as $signer) {
    $signerProtectedHeader = $signer->getProtectedHeader();   // ByteStringObject
    $kid = $signer->getUnprotectedHeaderParameter(4);         // ?CBORObject
    $signatureValue = $signer->getSignature();                // ByteStringObject
}
```

!!! warning

    Each signature of a `COSE_Sign` covers the `Signature` structure of
    [RFC 9052 §4.4](https://datatracker.ietf.org/doc/html/rfc9052#section-4.4), which carries the protected bucket of the
    message **and** the one of the signer's own entry, not the `Signature1` structure a `COSE_Sign1` uses:

    ```php
    use Cose\Signature\Signature;

    $toBeSigned = Signature::create(
        $coseSign->getProtectedHeader(),   // body_protected
        $signer->getProtectedHeader(),     // sign_protected
        $coseSign->getPayload(),
    );
    $isValid = $algorithm->verify((string) $toBeSigned, $key, $signer->getSignature()->getValue());
    ```

    RFC 9052 §4.1 writes the list as `[+ COSE_Signature]`: at least one entry, each a `[bstr, map, bstr]` array. The CBOR
    layer only checks that the item is a list, so `CoseSignature::all()` is where that rule is applied: it rejects an
    empty list and any entry of another shape.

[`examples/02-sign-multiple-signers.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/02-sign-multiple-signers.php) signs with two signers and shows
why `Signature` carries `sign_protected`.

A signature added *after* a message is finalized (a notary's, a timestamping service's) is a countersignature, not
another signer: it lives in the unprotected bucket and is computed over a different structure. See
[Countersignatures](../signing/countersignatures.md). A signature over the digest of a payload kept elsewhere is a
[hash envelope](../header-parameters/hash-envelope.md).
