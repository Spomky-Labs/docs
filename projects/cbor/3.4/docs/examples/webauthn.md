---
description: Reading the CBOR structures a WebAuthn credential is made of
---

# WebAuthn and FIDO2

A WebAuthn registration hands the server an attestation object: CBOR, and the reason this library exists.
It is a map of three entries — the attestation format, the statement itself, and the authenticator data as
raw bytes:

```php
use CBOR\Decoder;
use CBOR\MapObject;
use CBOR\StringStream;

$decoder = Decoder::create();

$attestationObject = $decoder->decode(StringStream::create($binaryData));

if (! $attestationObject instanceof MapObject) {
    throw new RuntimeException('An attestation object is a CBOR map');
}

$format = $attestationObject->get('fmt')->normalize();       // "packed", "none", "tpm"…
$statement = $attestationObject->get('attStmt');             // a map, whose shape depends on the format
$authenticatorData = $attestationObject->get('authData')->getValue(); // bytes, left as they are
```

Keep `authData` as the byte string it is. It is signed, so a single byte re-encoded differently breaks the
signature; parse it as the binary structure WebAuthn specifies — flags, counter, credential — not as CBOR.

The credential public key, on the other hand, sits inside `authData` and *is* CBOR: a COSE key, a map
whose keys are negative and positive integers rather than strings.

```php
// $credentialPublicKey are the bytes that follow the credential id in authData
$key = $decoder->decode(StringStream::create($credentialPublicKey));

$kty = $key->get(1)->normalize();  // key type
$alg = $key->get(3)->normalize();  // algorithm
```

!!! tip "Do not write a WebAuthn server by hand"

    [web-auth/webauthn-framework](https://github.com/web-auth/webauthn-framework) does all of the above,
    with the attestation statement formats, the verification of the signature and the checks the
    specification asks for. It uses this library underneath. The code here is for reading what is on the
    wire, or for debugging what a client sent.
