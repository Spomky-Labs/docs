---
description: 'Why a tag computed over the bare payload is bound to nothing.'
---

# The tag covers the MAC_structure

!!! warning

    The tag of a `COSE_Mac0` or `COSE_Mac` is **not** a MAC of the payload. It is computed over the `MAC_structure` of
    [RFC 9052 §6.3](https://datatracker.ietf.org/doc/html/rfc9052#section-6.3), which binds the tag to the protected
    header and to the message type:

    ```php
    use Cose\Mac\Mac0Structure;
    use Cose\Mac\MacStructure;

    // COSE_Mac0: context "MAC0"
    $toBeMaced = Mac0Structure::create($coseMac0->getProtectedHeader(), $coseMac0->getPayload());
    $macTag = $algorithm->hash((string) $toBeMaced, $key);

    // COSE_Mac: context "MAC", where the same header and payload give a different tag
    $toBeMaced = MacStructure::create($coseMac->getProtectedHeader(), $coseMac->getPayload());
    $isValid = $algorithm->verify((string) $toBeMaced, $key, $coseMac->getTag()->getValue());
    ```

    `Cose\Algorithm\Mac\Mac::hash()` and `verify()` authenticate exactly the bytes they are given, so passing
    `getPayload()->getValue()` straight to them produces a tag bound to nothing and interoperable with no other
    implementation. For AES-CBC-MAC the structure is also what makes the algorithm safe to use at all, see
    [MAC algorithms](../algorithms/mac-algorithms.md).
