---
description: 'Multiple recipients, each given the content encryption key by its own key management algorithm.'
---

# COSE_Encrypt

The content layer is the same, under the `"Encrypt"` context, with a content encryption key (CEK) drawn at random
and wrapped for each recipient:

```php
use CBOR\ListObject;
use CBOR\Tag\CoseEncryptTag;
use Cose\Encryption\EncryptStructure;
use Cose\Structure\CoseRecipient;

$ciphertext = EncryptStructure::create($protectedHeader)->encrypt($algorithm, $contentEncryptionKey, $plaintext, $nonce);

$recipients = ListObject::create([
    ListObject::create([/* recipient 1: protected, unprotected, wrapped CEK */]),
    ListObject::create([/* recipient 2 */]),
]);

$coseEncrypt = CoseEncryptTag::create(ListObject::create([
    $protectedHeader,
    $unprotectedHeader,
    ByteStringObject::create($ciphertext),
    $recipients,
]));

// Reading them back as checked views; a recipient may carry recipients of its own
foreach (CoseRecipient::all($coseEncrypt->getRecipients()) as $recipient) {
    $kid = $recipient->getUnprotectedHeaderParameter(4);
    $wrappedKey = $recipient->hasDetachedCiphertext() ? null : $recipient->getCiphertext();
    $nested = $recipient->getRecipients(); // list<CoseRecipient>
}
```

!!! warning

    The additional authenticated data of the content encryption is the `Enc_structure` of
    [RFC 9052 §5.3](https://datatracker.ietf.org/doc/html/rfc9052#section-5.3), not the protected header on its own.
    `Encrypt0Structure` and `EncryptStructure` differ by their context string only, and that difference is
    authenticated: a ciphertext produced for a `COSE_Encrypt` does not open as a `COSE_Encrypt0`. For a recipient
    layer, the structure is `RecipientStructure::forEncryptRecipient()` (`"Enc_Recipient"`):

    ```php
    use Cose\Encryption\Encrypt0Structure;
    use Cose\Encryption\EncryptStructure;
    use Cose\Encryption\RecipientStructure;

    $aad = (string) EncryptStructure::create($coseEncrypt->getProtectedHeader());               // "Encrypt"
    $aad = (string) Encrypt0Structure::create($coseEncrypt0->getProtectedHeader());             // "Encrypt0"
    $aad = (string) RecipientStructure::forEncryptRecipient($recipient->getProtectedHeader());  // "Enc_Recipient"
    ```

    RFC 9052 §5.1 writes the list as `[+COSE_recipient]`: at least one entry, each a
    `[bstr, map, bstr / nil, ? [+ COSE_recipient]]` array. `CoseRecipient::all()` applies that rule, nested levels
    included.

The recipient entries are filled by the key management algorithms of RFC 9053 §5 and §6, and
`EncryptStructure::encryptFor()` runs the whole of it (draw the CEK, wrap or derive it for each recipient, encrypt
the content, assemble the message) in one call:

```php
use Cose\Algorithm\ContentEncryption\A128GCM;
use Cose\Algorithm\KeyManagement\A256KW;
use Cose\Algorithm\KeyManagement\ECDH_ES_A128KW;
use Cose\Encryption\EncryptStructure;
use Cose\Encryption\Recipient;

$algorithm = A128GCM::create();
$coseEncrypt = EncryptStructure::create($protectedHeader)->encryptFor($algorithm, $plaintext, random_bytes(12), [
    Recipient::create(A256KW::create(), $sharedKek, null, $kidHeader),  // a Symmetric key the parties share
    Recipient::create(ECDH_ES_A128KW::create(), $bobPublicKey),         // Bob's EC2 or OKP public key
]); // CBOR\Tag\CoseEncryptTag: the IV is in its unprotected bucket, each COSE_recipient carries its "alg"
```

Opening it is the reverse, one recipient at a time: the recipient's own key, the algorithm its headers announce,
and a `RecipientLayer` that says what the recovered key is for:

```php
use Cose\Algorithm\KeyManagement\KeyManagement;
use Cose\Algorithm\KeyManagement\RecipientLayer;
use Cose\Encryption\InitializationVector;
use Cose\Key\SymmetricKey;
use Cose\Structure\CoseHeaders;

$entries = CoseRecipient::all($coseEncrypt->getRecipients());
$mine = $entries[1]; // located by "kid", by the ephemeral key, or however the application names its recipients
$keyManagement = $manager->get((int) $mine->headers()->getHeaderParameter(1)?->normalize());
assert($keyManagement instanceof KeyManagement);

$cek = $keyManagement->recoverKey(RecipientLayer::fromRecipient($mine, $algorithm, null, count($entries)), $bobPrivateKey);
$plaintext = EncryptStructure::create($coseEncrypt->getProtectedHeader())->decrypt(
    $algorithm,
    SymmetricKey::create([SymmetricKey::TYPE => SymmetricKey::TYPE_OCT, SymmetricKey::DATA_K => $cek]),
    $coseEncrypt->getCiphertext()->getValue(),
    InitializationVector::resolve(CoseHeaders::fromMessage($coseEncrypt), $algorithm->nonceLength())
);
```

See [Key management](../key-management/README.md) for the eighteen algorithms, the rules each family enforces, and the
parameters of a static-static agreement; and
[`examples/05-encrypt-recipients.php`](https://github.com/web-auth/cose-lib/blob/HEAD/examples/05-encrypt-recipients.php) for the whole of it, nested recipients
included.
