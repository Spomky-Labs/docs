---
title: JWT Framework
description: The published security advisories of JWT Framework, their severity and the versions that fix each one.
---

# JWT Framework

The published advisories of [web-token/jwt-framework](https://github.com/web-token/jwt-framework/security/advisories), the newest first.
Each one names the packages and the version ranges it affects. The latest release of every supported
line carries every fix.

| Published | Advisory | Severity | Fixed in |
|---|---|---|---|
| 2026-11-08 | [Rejected JWE tokens write decryption keys into exception stack traces (4.2.1 to 4.2.5)](https://github.com/web-token/jwt-framework/security/advisories/GHSA-7hp7-mg7x-hww4) | Medium | 4.2.6 |
| 2026-11-08 | [ECDH-ES: an oversized "epk" coordinate costs seconds to minutes of CPU per token when PHP has no GMP extension](https://github.com/web-token/jwt-framework/security/advisories/GHSA-wwq7-mh3q-hwrh) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption-algorithm-ecdh-es` |
| 2026-11-08 | [RSA keys of any size are accepted: a key chosen by the sender of a token costs seconds of CPU per operation (RSA-PSS and RSA encryption, and every RSA algorithm without GMP)](https://github.com/web-token/jwt-framework/security/advisories/GHSA-96f8-m4jr-72xj) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-signature-algorithm-rsa`, `web-token/jwt-encryption-algorithm-rsa` |
| 2026-11-08 | [RSA-OAEP accepts an encrypted key made of several RSA blocks, enabling recovery of another JWE's content encryption key through a decryption oracle](https://github.com/web-token/jwt-framework/security/advisories/GHSA-wwcr-82mc-w3pw) | Medium | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption-algorithm-rsa` |
| 2026-11-08 | [Direct encryption (dir) does not check the key size: with a key of half the required size, AES-CBC-HMAC content is encrypted under an all-zero AES key and anyone holding the token can read it](https://github.com/web-token/jwt-framework/security/advisories/GHSA-jc6j-46g2-xwqc) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption` |
| 2026-11-08 | [AES key wrapping accepts oct keys shorter than the algorithm key size and pads them with zero bytes: an empty key wraps every CEK under an all-zero key](https://github.com/web-token/jwt-framework/security/advisories/GHSA-4mxj-75j2-j8hc) | Medium | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption-algorithm-aeskw`, `web-token/jwt-encryption-algorithm-aesgcmkw`, `web-token/jwt-encryption-algorithm-experimental` |
| 2026-11-08 | [dir, ECDH-ES and ECDH-SS accept a non-empty JWE Encrypted Key, so token strings are malleable](https://github.com/web-token/jwt-framework/security/advisories/GHSA-5cc5-v8qv-6cw7) | Low | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption` |
| 2026-11-08 | [JWE and JWS loaders try every recipient or signature of a token, so a small token multiplies the PBES2 iteration cap (denial of service)](https://github.com/web-token/jwt-framework/security/advisories/GHSA-3vqw-452c-g726) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-encryption`, `web-token/jwt-signature` |
| 2026-11-08 | [JWS and JWE serializers decode attacker-controlled JSON without bounds before verification (CPU and memory denial of service)](https://github.com/web-token/jwt-framework/security/advisories/GHSA-2xq2-pp89-x7fr) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-signature`, `web-token/jwt-encryption` |
| 2026-11-08 | [Denial of service: parsing a JWS in the JSON General serialization takes a time quadratic in its number of signatures](https://github.com/web-token/jwt-framework/security/advisories/GHSA-jgv7-g4jg-6hqv) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-signature` |
| 2026-11-08 | [RSA private key recoverable through a timing side channel in RSA-OAEP and RSA1_5 decryption](https://github.com/web-token/jwt-framework/security/advisories/GHSA-2qpx-pwmq-r27r) | High | 3.4.13, 4.0.9, 4.1.11, 4.2.6<br>no fix for `web-token/jwt-core` |
| 2026-10-31 | [ECDH-ES derives at most 256 bits of key material: with A256CBC-HS512 the content is encrypted under an all-zero AES key and anyone holding the token can read it](https://github.com/web-token/jwt-framework/security/advisories/GHSA-5pj7-wx9m-cjh6) | High | 3.4.12, 4.0.8, 4.1.10, 4.2.4<br>no fix for `web-token/jwt-encryption-algorithm-ecdh-es` |
| 2026-10-31 | [AES-GCM decryption accepts any authentication tag length: a holder of one valid JWE can brute force a 1-byte tag in at most 256 requests and rewrite the plaintext](https://github.com/web-token/jwt-framework/security/advisories/GHSA-j265-mg9q-wpv9) | High | 3.4.11, 4.0.8, 4.1.10, 4.2.4<br>no fix for `web-token/jwt-encryption`, `web-token/jwt-encryption-algorithm-aesgcm`, `web-token/jwt-encryption-algorithm-aesgcmkw` |
| 2026-06-06 | [JWSVerifier uses algorithm from unprotected header, enabling algorithm confusion attacks](https://github.com/web-token/jwt-framework/security/advisories/GHSA-jc38-x7x8-2xc8) | High | 3.4.10, 4.0.7, 4.1.7 |
| 2026-06-06 | [RSA1_5 (RSAES-PKCS1-v1_5) decryption lacks implicit rejection, exposing a Bleichenbacher/Marvin padding oracle](https://github.com/web-token/jwt-framework/security/advisories/GHSA-5739-39v2-5754) | Medium | 3.4.10, 4.0.7, 4.1.7 |
| 2026-06-06 | [Chacha20Poly1305 key-encryption algorithm discards the Poly1305 authentication tag, performing no authentication on decryption](https://github.com/web-token/jwt-framework/security/advisories/GHSA-6vvh-pxr4-25r7) | Medium | 3.4.10, 4.0.7, 4.1.7 |
| 2026-06-06 | [PBES2-HS*+A*KW unwrap accepts an unbounded p2c iteration count, enabling CPU-amplification denial of service](https://github.com/web-token/jwt-framework/security/advisories/GHSA-3prj-6hqw-cm82) | High | 3.4.10, 4.0.7, 4.1.7 |
