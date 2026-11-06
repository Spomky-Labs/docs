---
description: 'The alg and key_ops restrictions a key management algorithm enforces.'
---

# Key restrictions

**Enforced by default**, as for the content encryption algorithms: RFC 9053 §6 makes the checks a MUST and the
classes are new. `alg`, when present, must match the identifier; `key_ops`, when present, must include `derive key`
or `derive bits` for the key of a derivation or an agreement, `wrap key` or `encrypt` to wrap and `unwrap key` or
`decrypt` to unwrap, and "MUST be empty for the public key" of an agreement (§6.3.1). `direct` enforces nothing: the
key is the content key itself, and the content encryption or MAC algorithm checks it when it uses it.
`withKeyRestrictionsEnforced(false)`, on an algorithm or through the `Manager`, turns it off; see
[Key restrictions](../keys/key-restrictions.md) for the mechanism.

```php
use Cose\Algorithm\KeyManagement\A128KW;
use Cose\Algorithm\KeyManagement\Direct;
use Cose\Algorithm\KeyManagement\DirectHKDF_SHA256;
use Cose\Algorithm\KeyManagement\ECDH_ES_A128KW;
use Cose\Algorithm\KeyManagement\ECDH_ES_HKDF256;
use Cose\Algorithm\KeyManagement\ECDH_SS_HKDF256;
use Cose\Algorithm\Manager;

$manager = Manager::create()->add(
    Direct::create(),
    DirectHKDF_SHA256::create(),
    A128KW::create(),
    ECDH_ES_HKDF256::create(),
    ECDH_SS_HKDF256::create(),
    ECDH_ES_A128KW::create(),
);
```

The `ecdh-direct-examples`, `ecdh-wrap-examples`, `hkdf-hmac-sha-examples`, `hkdf-aes-examples`,
`aes-wrap-examples`, `X25519-tests` and `enveloped-tests` fixtures of cose-wg/Examples, and the layered ones of
RFC 8152 Appendix B and C.5.4, are opened by the test suite, every intermediate the generator recorded
(`COSE_KDF_Context`, shared secret, KEK, CEK) compared on the way.
