---
description: 'A complete, runnable example: generate a key, issue a self-signed certificate, read it back.'
---

# A self-signed certificate

The shortest complete thing: one key, one name, one certificate.

## The key

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out key.pem
```

## The script

```php title="self-signed.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\CryptoTypes\AlgorithmIdentifier\Signature\SHA256WithRSAEncryptionAlgorithmIdentifier;
use SpomkyLabs\Pki\CryptoTypes\Asymmetric\PrivateKeyInfo;
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\Certificate\Extension\BasicConstraintsExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\KeyUsageExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectAlternativeNameExtension;
use SpomkyLabs\Pki\X509\Certificate\Extension\SubjectKeyIdentifierExtension;
use SpomkyLabs\Pki\X509\Certificate\TBSCertificate;
use SpomkyLabs\Pki\X509\Certificate\Validity;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;

$privateKeyInfo = PrivateKeyInfo::fromPEM(PEM::fromFile('key.pem'));
$publicKeyInfo = $privateKeyInfo->publicKeyInfo();

$name = Name::fromString('cn=example.com, o=ACME Ltd, c=FR');

// subject, key, issuer, validity. Self-signed: the subject is its own issuer.
$tbsCertificate = TBSCertificate::create(
    $name,
    $publicKeyInfo,
    $name,
    Validity::fromStrings('now', 'now + 1 year')
);

$tbsCertificate = $tbsCertificate->withAdditionalExtensions(
    BasicConstraintsExtension::create(true, false),
    KeyUsageExtension::create(
        true,
        KeyUsageExtension::DIGITAL_SIGNATURE | KeyUsageExtension::KEY_ENCIPHERMENT
    ),
    ExtendedKeyUsageExtension::create(false, ExtendedKeyUsageExtension::OID_SERVER_AUTH),
    SubjectAlternativeNameExtension::create(false, GeneralNames::create(
        DNSName::create('example.com'),
        DNSName::create('www.example.com')
    )),
    SubjectKeyIdentifierExtension::create(false, $publicKeyInfo->keyIdentifier())
);

// sign() draws a 20-octet random serial number, since none was set.
$certificate = $tbsCertificate->sign(
    SHA256WithRSAEncryptionAlgorithmIdentifier::create(),
    $privateKeyInfo
);

file_put_contents('cert.pem', $certificate->toPEM()->string());

echo "written: cert.pem\n";
```

```bash
php self-signed.php
```

## Reading it back

```php title="read.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\Certificate\Certificate;

$certificate = Certificate::fromPEM(PEM::fromFile('cert.pem'));
$tbs = $certificate->tbsCertificate();

printf("subject:   %s\n", $tbs->subject()->toString());
printf("issuer:    %s\n", $tbs->issuer()->toString());
printf("serial:    %s\n", $tbs->serialNumber());
printf("version:   v%d\n", $tbs->version() + 1);
printf("valid:     %s → %s\n",
    $tbs->validity()->notBefore()->dateTime()->format('c'),
    $tbs->validity()->notAfter()->dateTime()->format('c')
);
printf("key:       %s\n", $tbs->subjectPublicKeyInfo()->algorithmIdentifier()->name());
printf("signature: %s\n", $certificate->signatureAlgorithm()->name());

$extensions = $tbs->extensions();

if ($extensions->hasSubjectAlternativeName()) {
    foreach ($extensions->subjectAlternativeName()->names() as $name) {
        printf("alt name:  %s\n", $name->string());
    }
}

printf("self-issued: %s\n", $tbs->subject()->equals($tbs->issuer()) ? 'yes' : 'no');
printf("self-signed: %s\n", $certificate->verify($tbs->subjectPublicKeyInfo()) ? 'yes' : 'no');
```

Output:

```
subject:   cn=example.com,o=ACME Ltd,c=FR
issuer:    cn=example.com,o=ACME Ltd,c=FR
serial:    226837828384488469407726948667756172186701948421
version:   v3
valid:     2026-11-05T20:55:35+00:00 → 2027-11-05T20:55:35+00:00
key:       rsaEncryption
signature: sha256WithRSAEncryption
alt name:  example.com
alt name:  www.example.com
self-issued: yes
self-signed: yes
```

`version()` returns 2 for a v3 certificate — the ASN.1 field is zero-based, hence the `+ 1` when
printing.

## Checking against OpenSSL

Worth doing once for any issuance path you write:

```bash
openssl x509 -in cert.pem -noout -text
openssl verify -CAfile cert.pem cert.pem      # a self-signed certificate as its own root
```

## Validating it as a path

A self-signed certificate is a path of one, and it is its own trust anchor:

```php
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

$path = CertificationPath::toTarget($certificate, CertificateBundle::create($certificate));
$result = $path->validate(PathValidationConfig::defaultConfig());

echo $result->certificate()->tbsCertificate()->subject()->toString(), "\n";
```

!!! note "Trusting it only proves you trust it"

    The anchor here is the certificate itself, which is sound only because *you* put it in the bundle.
    That is the whole point of [naming the anchor](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input):
    doing the same with a certificate a peer sent would prove nothing at all.

## Next

[A small certificate authority](a-small-certificate-authority.md), where the issuer and the subject stop
being the same party.
