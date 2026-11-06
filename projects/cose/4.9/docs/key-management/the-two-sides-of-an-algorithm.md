---
description: 'What the sender computes and what the recipient computes, for each family.'
---

# The two sides of an algorithm

Every algorithm has a receiving side, `recoverKey()`, and a sending side, `protectKey()`, both run against a
`RecipientLayer`: the headers and the ciphertext of the `COSE_recipient`, and what the algorithm needs to know about
the key it protects: the algorithm that key is for and its length, which [RFC 9053 §5.2](https://datatracker.ietf.org/doc/html/rfc9053#section-5.2)
binds into the derived key through the `COSE_KDF_Context`. That key is the content encryption or MAC algorithm of the
message for a recipient of the content layer, and the key wrap of the recipient above for a nested one
([RFC 9052 Appendix B](https://datatracker.ietf.org/doc/html/rfc9052#appendix-B)).

```php
use Cose\Algorithm\KeyManagement\RecipientLayer;
use Cose\Structure\CoseHeaders;

// Receiving: the layer of a decoded COSE_recipient, for the content algorithm, among $count recipients
$layer = RecipientLayer::fromRecipient($coseRecipient, $contentAlgorithm, null, $count);
$key = $keyManagement->recoverKey($layer, $recipientKey);        // the CEK, or the KEK of the recipient above

// Sending: the layer of the recipient the sender is about to write
$layer = RecipientLayer::create(CoseHeaders::of($protected, $unprotected), $contentAlgorithm, null, $count);
$protectedKey = $keyManagement->protectKey($layer, $recipientKey, $cek); // ProtectedKey
$protectedKey->key();              // the key of the layer below: the $cek given, or the one a direct algorithm derived
$protectedKey->headerParameters(); // to merge into the unprotected bucket of the recipient: the "ephemeral key"
$protectedKey->ciphertext();       // the "ciphertext" field of the COSE_recipient: the wrapped key, or h''
```

The recipient's key is the shared symmetric secret for the direct encryption and key wrap families, and the
recipient's EC2 or OKP key for the key agreement family, private on the receiving side, public on the sending side.
