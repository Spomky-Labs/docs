---
description: A root, an intermediate, a certificate issued from a request, and the path that validates it.
---

# A small certificate authority

A root, an intermediate under it, and an end-entity certificate issued from a certification request —
then the path that validates the result. Enough to stand up an internal PKI, and enough to show every
decision an issuer makes.

## The keys

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out root.key
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out intermediate.key
openssl genpkey -algorithm EC -pkeyopt ec_paramgen_curve:P-256 -out server.key
```

## The root

```php title="1-root.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectKeyIdentifierExtension;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;

$rootKey = PrivateKeyInfo::fromPEM(PEM::fromFile('root.key'));
$rootName = Name::fromString('cn=ACME Root CA, o=ACME Ltd, c=FR');

$tbs = TBSCertificate::create(
    $rootName,
    $rootKey->publicKeyInfo(),
    $rootName,                                  // self-issued
    Validity::fromStrings('now', 'now + 10 years')
);

$tbs = $tbs->withAdditionalExtensions(
    // critical, cA, pathLenConstraint: one intermediate may follow, then end entities only
    BasicConstraintsExtension::create(true, true, 1),
    KeyUsageExtension::create(true, KeyUsageExtension::KEY_CERT_SIGN | KeyUsageExtension::CRL_SIGN),
    SubjectKeyIdentifierExtension::create(false, $rootKey->publicKeyInfo()->keyIdentifier())
);

$root = $tbs->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $rootKey);

file_put_contents('root.pem', $root->toPEM()->string());
```

A root is self-issued, asserts `cA:TRUE`, and its `keyUsage` carries `keyCertSign`. Path validation
refuses an intermediate missing either, so these are not decoration.

## The intermediate

```php title="2-intermediate.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\Certificate\Certificate;
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraints\GeneralSubtree;
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraints\GeneralSubtrees;
use SpomkyLabs\Pki\X509\Certificate\Extension\NameConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectKeyIdentifierExtension;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;

$rootKey = PrivateKeyInfo::fromPEM(PEM::fromFile('root.key'));
$root = Certificate::fromPEM(PEM::fromFile('root.pem'));

$intermediateKey = PrivateKeyInfo::fromPEM(PEM::fromFile('intermediate.key'));
$intermediatePublicKey = $intermediateKey->publicKeyInfo();

$tbs = TBSCertificate::create(
    Name::fromString('cn=ACME Issuing CA, o=ACME Ltd, c=FR'),
    $intermediatePublicKey,
    Name::create(),                             // replaced by withIssuerCertificate()
    Validity::fromStrings('now', 'now + 5 years')
);

// Sets the issuer DN from the root's subject, and adds an authorityKeyIdentifier.
$tbs = $tbs->withIssuerCertificate($root)->withRandomSerialNumber();

$tbs = $tbs->withAdditionalExtensions(
    BasicConstraintsExtension::create(true, true, 0),   // may issue end entities only
    KeyUsageExtension::create(true, KeyUsageExtension::KEY_CERT_SIGN | KeyUsageExtension::CRL_SIGN),
    SubjectKeyIdentifierExtension::create(false, $intermediatePublicKey->keyIdentifier()),
    // This intermediate may only ever vouch for names under example.com.
    NameConstraintsExtension::create(
        true,
        GeneralSubtrees::create(GeneralSubtree::create(DNSName::create('example.com')))
    )
);

// Signed with the ROOT's key: the issuer signs, not the subject.
$intermediate = $tbs->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $rootKey);

file_put_contents('intermediate.pem', $intermediate->toPEM()->string());
```

!!! note "`withAdditionalExtensions()`, not `withExtensions()`"

    `withIssuerCertificate()` already added the `authorityKeyIdentifier`.
    `withExtensions()` would replace the whole set and throw it away.

The `nameConstraints` extension is what makes a delegated CA safe to hand out: whatever this
intermediate signs, path validation refuses it if the name falls outside `example.com`.

## The request, from the server's side

```php title="3-request.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\ECDSAWithSHA256AlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectAlternativeNameExtension;
use SpomkyLabs\Pki\X509\Certificate\Extensions;
use SpomkyLabs\Pki\X509\CertificationRequest\CertificationRequestInfo;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

$serverKey = PrivateKeyInfo::fromPEM(PEM::fromFile('server.key'));

$cri = CertificationRequestInfo::create(
    Name::fromString('cn=www.example.com, o=ACME Ltd, c=FR'),
    $serverKey->publicKeyInfo()
);

$cri = $cri->withExtensionRequest(Extensions::create(
    SubjectAlternativeNameExtension::create(false, GeneralNames::create(
        DNSName::create('www.example.com'),
        DNSName::create('example.com')
    ))
));

// An EC key needs an ECDSA algorithm.
$csr = $cri->sign(ECDSAWithSHA256AlgorithmIdentifier::create(), $serverKey);

file_put_contents('server.csr', $csr->toPEM()->string());
```

## Issuing from the request, from the CA's side

```php title="4-issue.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X509\Certificate\Certificate;
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\Extension;
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;
use SpomkyLabs\Pki\X509\CertificationRequest\CertificationRequest;

$intermediateKey = PrivateKeyInfo::fromPEM(PEM::fromFile('intermediate.key'));
$intermediate = Certificate::fromPEM(PEM::fromFile('intermediate.pem'));

$csr = CertificationRequest::fromPEM(PEM::fromFile('server.csr'));

// 1. fromCSR() does NOT verify the signature. You do.
if (! $csr->verify()) {
    throw new RuntimeException('The request is not signed by the key it carries.');
}

// 2. Your policy decides whether this requester may have this name. Here, we accept the
//    requested one; a real CA proves control of the domain first.
$subject = $csr->certificationRequestInfo()->subject();

// 3. An explicit allow list. Only subjectAltName is copied; everything else is dropped.
$tbs = TBSCertificate::fromCSR($csr, [Extension::OID_SUBJECT_ALT_NAME]);

// 4. The issuer sets everything that decides what this certificate may do.
$tbs = $tbs
    ->withSubject($subject)
    ->withIssuerCertificate($intermediate)
    ->withValidity(Validity::fromStrings('now', 'now + 90 days'))
    ->withRandomSerialNumber()
    ->withAdditionalExtensions(
        BasicConstraintsExtension::create(true, false),
        KeyUsageExtension::create(
            true,
            KeyUsageExtension::DIGITAL_SIGNATURE | KeyUsageExtension::KEY_ENCIPHERMENT
        ),
        ExtendedKeyUsageExtension::create(false, ExtendedKeyUsageExtension::OID_SERVER_AUTH)
    );

// 5. Signed with the intermediate's key.
$server = $tbs->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $intermediateKey);

file_put_contents('server.pem', $server->toPEM()->string());
```

Those five numbered steps are the whole of
[Issuing from a request](../certification-requests/issuing-from-a-request.md). Leaving out the allow list
in step 3 would raise a deprecation notice and copy every requested extension that is not forbidden —
`subjectAltName` included, which is the one that names identities.

## Validating the result

```php title="5-validate.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathValidationException;
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

$root = Certificate::fromPEM(PEM::fromFile('root.pem'));
$intermediate = Certificate::fromPEM(PEM::fromFile('intermediate.pem'));
$server = Certificate::fromPEM(PEM::fromFile('server.pem'));

$trustAnchors = CertificateBundle::create($root);              // what you trust
$intermediates = CertificateBundle::create($intermediate);     // what bridges the gap

$path = CertificationPath::toTarget($server, $trustAnchors, $intermediates);

$config = PathValidationConfig::defaultConfig()
    ->withAllowedSignatureAlgorithms(...PathValidationConfig::HARDENED_ALLOWED_SIGNATURE_ALGORITHMS)
    ->withMinimumRSAKeySize(PathValidationConfig::HARDENED_MINIMUM_RSA_KEY_SIZE);

try {
    $result = $path->validate($config);
} catch (PathValidationException $e) {
    exit('invalid: ' . $e->getMessage() . "\n");
}

printf("path length: %d\n", count($path));

foreach ($path as $i => $certificate) {
    printf("  [%d] %s\n", $i, $certificate->tbsCertificate()->subject()->toString());
}

printf("validated:   %s\n", $result->certificate()->tbsCertificate()->subject()->toString());
printf("key:         %s\n", $result->getPublicKeyInfo()->algorithmIdentifier()->name());
```

Output:

```
path length: 3
  [0] cn=ACME Root CA,o=ACME Ltd,c=FR
  [1] cn=ACME Issuing CA,o=ACME Ltd,c=FR
  [2] cn=www.example.com,o=ACME Ltd,c=FR
validated:   cn=www.example.com,o=ACME Ltd,c=FR
key:         ecPublicKey
```

The path runs anchor-first. The hardened configuration passes here because everything was signed with
SHA-256 and 3072-bit RSA.

## Seeing the name constraint work

Issue a certificate for a name outside `example.com` from the same intermediate, and validation refuses
it:

Continuing in the context of `5-validate.php`, with `$intermediateKey` and `$serverKey` loaded and
`SubjectAlternativeNameExtension`, `GeneralNames` and `DNSName` imported:

```php
$tbs = TBSCertificate::create(
    Name::fromString('cn=www.other.test'),
    $serverKey->publicKeyInfo(),
    Name::create(),
    Validity::fromStrings('now', 'now + 90 days')
);

$tbs = $tbs->withIssuerCertificate($intermediate)->withRandomSerialNumber()
    ->withAdditionalExtensions(
        BasicConstraintsExtension::create(true, false),
        // The dNSName constraint applies to THIS, not to the common name. See the note below.
        SubjectAlternativeNameExtension::create(false, GeneralNames::create(
            DNSName::create('www.other.test')
        ))
    );

$bad = $tbs->sign(SHA256WithRSAEncryptionAlgorithmIdentifier::create(), $intermediateKey);

$path = CertificationPath::create($root, $intermediate, $bad);
$path->validate($config->withTrustAnchor($root));
// PathValidationException: Name 'www.other.test' is not within the permitted subtrees.
```

The signature is perfectly good. The constraint is what stops it — which is the point of putting one on a
delegated CA.

!!! warning "A `dNSName` constraint does not constrain the common name"

    Name constraints are matched **by name type**. A `dNSName` subtree is compared against the DNS names
    of the `subjectAltName` extension; the subject DN is submitted as a `directoryName` and is therefore
    compared against `directoryName` subtrees only. The tags have to match for a name to be constrained
    at all.

    So the certificate above, **without** the `subjectAltName`, validates: `cn=www.other.test` is a
    directory name, no `directoryName` subtree exists to constrain it, and the `dNSName` subtree never
    looks at it. That is RFC 5280 behaviour, not a gap — the common name has not been an identity in the
    web PKI for years, which is exactly why `subjectAltName` is normative.

    To constrain the names in a DN as well, add a `directoryName` subtree:

    ```php
    use SpomkyLabs\Pki\X509\GeneralName\DirectoryName;

    GeneralSubtrees::create(
        GeneralSubtree::create(DNSName::create('example.com')),
        GeneralSubtree::create(DirectoryName::create(Name::fromString('o=ACME Ltd, c=FR')))
    );
    ```

    One more reason the issuer, not the requester, sets `subjectAltName`:
    [Issuing from a request](../certification-requests/issuing-from-a-request.md).

Note the `withTrustAnchor($root)` here: this path was built with `create()`, which does not know where
its first certificate came from. See
[Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input).

## What this CA does not do

No revocation, since nothing here issues a CRL and the library has no CRL support; no serial number
register, so keep your own if you intend to revoke anything; no key protection beyond the file
permissions on `root.key`. See
[What validation does not do](../certification-paths/what-validation-does-not-do.md).
