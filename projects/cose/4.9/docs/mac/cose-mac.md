---
description: 'A MAC with recipients, each carrying the authentication key.'
---

# COSE_Mac

The `COSE_Mac` structure carries the MAC key to its recipients the way `COSE_Encrypt` carries a content encryption
key: one `COSE_recipient` per recipient, filled by a [key management algorithm](../key-management/README.md).

```php
use CBOR\ListObject;
use CBOR\Tag\CoseMacTag;
use Cose\Mac\MacStructure;
use Cose\Structure\CoseRecipient;

// Context "MAC": the same header and payload give a different tag than under "MAC0"
$toBeMaced = MacStructure::create($protectedHeader, $payload);
$tag = ByteStringObject::create($algorithm->hash((string) $toBeMaced, $macKey));

$recipients = ListObject::create([
    ListObject::create([/* recipient 1: protected, unprotected, wrapped MAC key */]),
]);

$coseMac = CoseMacTag::create(ListObject::create([
    $protectedHeader,
    $unprotectedHeader,
    $payload,
    $tag,
    $recipients,
]));

// Reading the recipients back as checked views rather than raw lists
foreach (CoseRecipient::all($coseMac->getRecipients()) as $recipient) {
    $kid = $recipient->getUnprotectedHeaderParameter(4);
}
```

The `Enc_structure` a recipient of a `COSE_Mac` is computed over is `RecipientStructure::forMacRecipient()`
(`"Mac_Recipient"`); `RecipientLayer::fromRecipient()` takes the MAC algorithm as the algorithm of the layer below,
so that the `COSE_KDF_Context` binds the derived key to it. RFC 9052 §6.1 writes the list as `[+COSE_recipient]`:
at least one entry, which `CoseRecipient::all()` enforces, nested levels included.
