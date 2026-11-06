---
description: 'PublicKeyLoader: turning a certificate or a SubjectPublicKeyInfo into a COSE key.'
---

# Loading a key from a certificate

`Cose\Key\PublicKeyLoader` turns the key of an X.509 certificate, or a bare SubjectPublicKeyInfo, into a
`Cose\Key\Key`. Both accept PEM or DER, and both cover RSA (including RSASSA-PSS keys), the elliptic curves this
library names (P-256, secp256k1, P-384, P-521 and the four brainpool curves, a compressed point included), the
RFC 8410 curves, and the ML-DSA keys of [RFC 9881](https://www.rfc-editor.org/rfc/rfc9881.html), read into an
`AkpKey` carrying the `alg` the OID names. A certificate *signed* with ML-DSA cannot be read yet: spomky-labs/pki-framework
does not know the ML-DSA signature algorithm identifiers; a certificate holding an ML-DSA key and signed by a
classical CA is, see [ML-DSA](../algorithms/ml-dsa.md).

```php
use Cose\Key\PublicKeyLoader;

$key = PublicKeyLoader::fromCertificate($certificatePem);
$key = PublicKeyLoader::fromSubjectPublicKeyInfo($spkiDer);
```

`CertificateSignatureVerifier` does the conversion and the verification in one call, see
[Verifying with a certificate](../signing/verifying-with-a-certificate.md).
