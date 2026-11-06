---
description: 'A COSE signature or MAC never covers the payload alone: it covers a structure that binds the protected header and the message type.'
---

# Cryptographic structures

A COSE signature or MAC never covers the payload on its own. It covers a **structure** that also binds the
protected header and the message type, so a tag computed for a `COSE_Mac0` cannot be replayed on a
`COSE_Mac`, and a signature made for one signer of a `COSE_Sign` cannot be lifted into a `COSE_Sign1`. An
encryption likewise authenticates a structure rather than the bare protected header. These structures are
what this library builds; casting one to string yields the CBOR bytes to hand to the algorithm.

| RFC 9052 | Class | Context | Fields after the context |
|---|---|---|---|
| §4.4 `Sig_structure` | `Cose\Signature\Signature1` | `"Signature1"` | body_protected, external_aad, payload |
| §4.4 `Sig_structure` | `Cose\Signature\Signature` | `"Signature"` | body_protected, **sign_protected**, external_aad, payload |
| §6.3 `MAC_structure` | `Cose\Mac\Mac0Structure` | `"MAC0"` | protected, external_aad, payload |
| §6.3 `MAC_structure` | `Cose\Mac\MacStructure` | `"MAC"` | protected, external_aad, payload |
| §5.3 `Enc_structure` | `Cose\Encryption\Encrypt0Structure` | `"Encrypt0"` | protected, external_aad |
| §5.3 `Enc_structure` | `Cose\Encryption\EncryptStructure` | `"Encrypt"` | protected, external_aad |
| §5.3 `Enc_structure` | `RecipientStructure::forEncryptRecipient()` | `"Enc_Recipient"` | protected, external_aad |
| §5.3 `Enc_structure` | `RecipientStructure::forMacRecipient()` | `"Mac_Recipient"` | protected, external_aad |
| §5.3 `Enc_structure` | `RecipientStructure::forNestedRecipient()` | `"Rec_Recipient"` | protected, external_aad |
| RFC 9338 §3.3 `Countersign_structure` | `Cose\Signature\Countersign::full()` | `"CounterSignature"` / `"CounterSignatureV2"` | body_protected, **sign_protected**, external_aad, payload, ? other_fields |
| RFC 9338 §3.3 `Countersign_structure` | `Cose\Signature\Countersign::abbreviated()` | `"CounterSignature0"` / `"CounterSignature0V2"` | body_protected, external_aad, payload, ? other_fields |

```php
use Cose\Mac\Mac0Structure;
use Cose\Signature\Signature1;

// Signing and verifying a COSE_Sign1
$toBeSigned = Signature1::create($protectedHeaderAsBytes, $payload);
$signature = $algorithm->sign((string) $toBeSigned, $privateKey);
$isValid = $algorithm->verify((string) $toBeSigned, $publicKey, $signature);

// Authenticating a COSE_Mac0: the same shape, a different context string
$toBeMaced = Mac0Structure::create($protectedHeaderAsBytes, $payload);
$macTag = $macAlgorithm->hash((string) $toBeMaced, $symmetricKey);
```

!!! warning

    `Cose\Algorithm\Mac\Mac::hash()` and `verify()` authenticate exactly the bytes they are given. Passing
    `getPayload()->getValue()` straight to them produces a tag bound to no header, no algorithm and no
    message type, which no other implementation will accept.

## The protected header is passed as bytes

The protected header is passed as the **byte string the message carries**, not as a map: the structure has
to embed it verbatim, or the signature no longer verifies. `HeaderMapHelper::encodeProtected()` produces
those bytes from a map, applying the RFC 9052 §3 rules on the way out: an empty map becomes `h''` rather
than `h'a0'`, and the labels are checked (§1.5, §9).

There is one exception, and the structures apply it themselves. §3 lets a sender write an empty protected
bucket either as the zero-length byte string `h''` or as an empty map wrapped in a byte string, `h'a0'`,
and requires recipients to accept both; §§4.4, 5.3 and 6.3 then define the protected field of every
structure with "If there are no protected attributes, a zero-length byte string is used". A message
carrying `h'a0'` is therefore verified over `h''`, the bytes its sender computed, whichever form travels
on the wire. `CoseStructure::emptyOrSerializedMap()` is that rule, and only `h'a0'` is affected: a
non-empty bucket is never re-encoded.

Every structure takes the optional `external_aad` as its last argument, see
[External additional authenticated data](external-additional-authenticated-data.md). The
`Countersign_structure` is computed over a finalized message rather than by it; see
[Countersignatures](../signing/countersignatures.md).
