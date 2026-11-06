---
description: Validating a certificate chain a peer sent against a trust store you control, and the checks validation leaves to you.
---

# Verifying a TLS chain

The case most applications actually have: a peer sent a chain, you hold a trust store, and you need to
decide whether to believe it.

This example does the whole thing, including the parts path validation does not do.

## Getting a chain to work with

```bash
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null \
  | sed -n '/-----BEGIN CERTIFICATE-----/,/-----END CERTIFICATE-----/p' > chain.pem
```

The leaf comes first, then the intermediates the server chose to send. Roots are usually not sent.

## The script

```php title="verify-chain.php" linenums="1"
<?php

declare(strict_types=1);

require 'vendor/autoload.php';

use SpomkyLabs\Pki\ASN1\Element;
use SpomkyLabs\Pki\CryptoEncoding\PEMBundle;
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;
use SpomkyLabs\Pki\X509\Certificate\Extension\ExtendedKeyUsageExtension;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathBuildingException;
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathValidationException;
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;
use SpomkyLabs\Pki\X509\GeneralName\GeneralName;

$hostname = 'example.com';

// A real X.509 structure rarely nests deeper than ten levels; 64 is the default.
Element::setMaxNestingDepth(16);

// ---------------------------------------------------------------- the trust store

// Yours, not the system's: the library reads no trust store of its own.
$trustAnchors = CertificateBundle::fromPEMBundle(
    PEMBundle::fromFile('/etc/ssl/certs/ca-certificates.crt')
);

// ---------------------------------------------------------------- what the peer sent

$material = file_get_contents('chain.pem');

// Bound the input before you decode it: the library decodes the string you hand it.
if (strlen($material) > 64 * 1024) {
    exit("chain too large\n");
}

$sent = PEMBundle::fromString($material);

if (count($sent) > 10) {
    exit("too many certificates in the chain\n");
}

$chain = CertificateBundle::fromPEMBundle($sent);
$leaf = $chain->all()[0];                  // the peer puts its own certificate first

// ---------------------------------------------------------------- build and validate

$config = PathValidationConfig::defaultConfig()
    ->withAllowedSignatureAlgorithms(...PathValidationConfig::HARDENED_ALLOWED_SIGNATURE_ALGORITHMS)
    ->withMinimumRSAKeySize(PathValidationConfig::HARDENED_MINIMUM_RSA_KEY_SIZE);

try {
    // The path is headed by a certificate from YOUR bundle. The peer's certificates
    // only bridge the gap.
    $path = CertificationPath::toTarget($leaf, $trustAnchors, $chain);
} catch (PathBuildingException $e) {
    exit('no path to a trust anchor: ' . $e->getMessage() . "\n");
}

try {
    $result = $path->validate($config);
} catch (PathValidationException $e) {
    exit('path does not validate: ' . $e->getMessage() . "\n");
}

printf("path validates, %d certificates:\n", count($path));

foreach ($path as $i => $certificate) {
    printf("  [%d] %s\n", $i, $certificate->tbsCertificate()->subject()->toString());
}

$validated = $result->certificate();

// ---------------------------------------------------------------- what validation did NOT do

// 1. The hostname. Path validation never looks at one.
$extensions = $validated->tbsCertificate()->extensions();

if (! $extensions->hasSubjectAlternativeName()) {
    exit("no subjectAltName: cannot identify the server\n");
}

$dnsNames = [];

foreach ($extensions->subjectAlternativeName()->names()->allOf(GeneralName::TAG_DNS_NAME) as $name) {
    $dnsNames[] = $name->name();
}

if (! matchesHostname($hostname, $dnsNames)) {
    exit(sprintf("certificate is for %s, not %s\n", implode(', ', $dnsNames), $hostname));
}

// 2. Extended key usage. RFC 5280's algorithm says nothing about it.
if (! $extensions->hasExtendedKeyUsage()
    || ! $extensions->extendedKeyUsage()->has(ExtendedKeyUsageExtension::OID_SERVER_AUTH)) {
    exit("not a TLS server certificate\n");
}

// 3. Revocation. The library never opens a connection, so a revoked certificate
//    validates. This is where YOUR CRL or OCSP check goes.
$tbs = $validated->tbsCertificate();
printf("check revocation for issuer=%s serial=%s\n", $tbs->issuer()->toString(), $tbs->serialNumber());

if ($extensions->hasCRLDistributionPoints()) {
    foreach ($extensions->crlDistributionPoints()->distributionPoints() as $point) {
        if ($point->hasFullName()) {
            foreach ($point->fullName()->names()->allOf(GeneralName::TAG_URI) as $uri) {
                printf("  CRL: %s\n", $uri->uri());
            }
        }
    }
}

printf("accepted for %s\n", $hostname);

/**
 * A deliberately minimal matcher: exact, or one leading wildcard label.
 *
 * Real rules are longer — trailing dots, internationalised domains, public suffixes, whether a
 * wildcard may appear anywhere but the leftmost label. Use your protocol's.
 *
 * @param string[] $dnsNames
 */
function matchesHostname(string $hostname, array $dnsNames): bool
{
    $hostname = strtolower(rtrim($hostname, '.'));

    foreach ($dnsNames as $name) {
        $name = strtolower(rtrim($name, '.'));

        if ($name === $hostname) {
            return true;
        }

        if (str_starts_with($name, '*.')) {
            $suffix = substr($name, 1);                    // ".example.com"
            $labels = substr($hostname, 0, -strlen($suffix));

            if (str_ends_with($hostname, $suffix) && $labels !== '' && ! str_contains($labels, '.')) {
                return true;
            }
        }
    }

    return false;
}
```

```bash
php verify-chain.php
```

Output, against a real server:

```
path validates, 4 certificates:
  [0] cn=SSL.com TLS ECC Root CA 2022,o=SSL Corporation,c=US
  [1] cn=SSL.com TLS Transit ECC CA R2,o=SSL Corporation,c=US
  [2] cn=Cloudflare TLS Issuing ECC CA 3,o=SSL Corporation,c=US
  [3] cn=example.com
check revocation for issuer=cn=Cloudflare TLS Issuing ECC CA 3,o=SSL Corporation,c=US serial=2569673129085639595562975411803018896
  CRL: http://c.cf-i.ssl.com/ae801ed1c55bb579d79208b0d772acfb8cc3a208.crl
accepted for example.com
```

Whose certificates those are will have changed by the time you run it; the shape of the output is the
point.

## What each part is for

**`toTarget()` and not `fromCertificateChain()`.** The path is headed by a certificate from your trust
store. `fromCertificateChain($chain)` would produce a path headed by whatever the peer put last, and
would then refuse to validate without an explicit anchor — correctly, because that is not a trust
decision. See
[Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input).

**The peer's certificates as `$intermediates`.** A certificate from that bundle can appear in the middle
of a path, never at its head. Passing the chain there is how you let the peer help you find a path
without letting them choose where it starts.

**The hardened configuration.** The defaults accept SHA-1 and 1024-bit RSA, for deployments that still
need to. A TLS client on the public internet does not. See
[Configuration](../certification-paths/configuration.md).

**The size and count bounds.** The decoder caps nesting depth; it does not cap the length of the string
or the number of blocks in a bundle. See
[Decoding untrusted input](../asn1/untrusted-input.md#what-you-have-to-bound).

**The three checks after validation.** Hostname, extended key usage, revocation. None of them is part of
RFC 5280 section 6.1, so none of them is part of `validate()`. The full list is in
[What validation does not do](../certification-paths/what-validation-does-not-do.md).

## What this is not

This is the certificate layer, not a TLS stack. It does not speak the protocol, negotiate anything,
check that the server proved possession of the key during the handshake, or implement the additional
requirements TLS itself imposes on certificates. For an actual TLS connection, let the TLS
implementation verify the chain; use this when you hold certificates outside a handshake — pinned
material, an enrolment flow, an audit, a chain in a token.
