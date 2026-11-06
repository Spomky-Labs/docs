---
description: 'How the nonce is resolved from the IV header parameter, the Partial IV and the Base IV of the key.'
---

# The nonce: IV and Partial IV

[RFC 9052 §3.1](https://datatracker.ietf.org/doc/html/rfc9052#section-3.1) gives a message two ways to carry its
nonce: the `IV` header parameter (label 5) holds it whole; the `Partial IV` (label 6) holds only the part that
changes from one message to the next, and the recipient completes it with the `Base IV` of the key (label 5 of the
key map, [§7.1](https://datatracker.ietf.org/doc/html/rfc9052#section-7.1)):

1. left-pad the Partial IV with zeros to the nonce length of the algorithm;
2. XOR it with the Base IV, itself a prefix of the nonce.

`InitializationVector::resolve()` does both, and rejects a layer carrying the two parameters at once (the RFC says
they "MUST NOT both be present in the same security layer") as well as an `IV` of the wrong length:

```php
use Cose\Encryption\InitializationVector;
use Cose\Key\SymmetricKey;
use Cose\Structure\CoseHeaders;

$key = SymmetricKey::create([
    SymmetricKey::TYPE => SymmetricKey::TYPE_OCT,
    SymmetricKey::DATA_K => $sharedSecret,
    SymmetricKey::BASE_IV => $baseIv, // h'89F52F65A1C58093' in RFC 9052 Appendix C.4.2
]);

// The recipient: from the message headers
$nonce = InitializationVector::resolve(CoseHeaders::fromMessage($message), $algorithm->nonceLength(), $key);

// The sender: from the counter it is about to send as Partial IV
$nonce = InitializationVector::fromPartialIv($counter, $baseIv, $algorithm->nonceLength());
```

!!! warning

    **A nonce reused under the same key is catastrophic for every algorithm here.** AES-GCM and ChaCha20/Poly1305 leak
    their authentication key, after which any message under that key can be forged; AES-CCM leaks the XOR of the two
    plaintexts. Draw the nonce with `random_bytes()` for each message, or send a strictly increasing counter as the
    `Partial IV`. The 7-byte nonce of the AES-CCM-64-* variants is too short for random draws to stay unique for long
    (a collision is expected after about 2^28 messages): use a counter with those.
