---
description: CertificateBundle as a trust store, CertificateChain as what a peer sent, and why they are different types.
---

# Bundles and chains

Two collections, and the difference is not cosmetic.

| Type | Is | Order |
|---|---|---|
| `CertificateBundle` | a **set**: a trust store, a pool of intermediates | none |
| `CertificateChain` | a **sequence**: what a peer sent, end entity first | significant |

A bundle is something you assembled. A chain is something you were given. Keeping them apart is how the
library stops a peer-supplied chain from being mistaken for a trust list; see
[Validating a path](../certification-paths/validating-a-path.md#the-trust-anchor-is-an-input).

## CertificateBundle

```php
use SpomkyLabs\Pki\CryptoEncoding\PEMBundle;
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;

$trustAnchors = CertificateBundle::create($rootA, $rootB);
$trustAnchors = CertificateBundle::fromPEMBundle(PEMBundle::fromFile('/etc/ssl/certs/ca-bundle.crt'));
$trustAnchors = CertificateBundle::fromPEMs(...$pems);

$trustAnchors = $trustAnchors->withCertificates($anotherRoot);
$trustAnchors = $trustAnchors->withPEM($pem);
$trustAnchors = $trustAnchors->withPEMBundle($pemBundle);

count($trustAnchors);
$trustAnchors->all();

foreach ($trustAnchors as $certificate) {
}
```

Immutable, like everything else: `with*()` returns a new bundle.

### Membership

```php
$bundle->contains($certificate);
```

`contains()` is an **exact** question: it compares encodings octet by octet, through
`Certificate::equals()`. Indexing by key identifier makes the lookup fast, but the answer is still an
exact match.

!!! note "It used to be looser, and that was a bug"

    The check was once on the serial number, the subject key identifier and the subject DN — three public
    values anyone can repeat. A certificate agreeing on those but differing in issuer, validity, every
    extension and the signature was reported as present, so `contains()` said yes for a certificate that
    was not in the bundle. If you need the looser grouping deliberately, ask
    `Certificate::hasEqualSubjectIdentity()` and know what it does not tell you.

### Lookup by key identifier

This is what [path building](../certification-paths/building-a-path.md) uses to find an issuer:

```php
$candidates = $bundle->allBySubjectKeyIdentifier($authorityKeyIdentifier);
```

A certificate is indexed twice: under the identifier **computed** from its public key, and under the one
its `subjectKeyIdentifier` extension **declares**, when the two differ.

The declared value is arbitrary data that nothing checks against the key. Indexing on it alone meant that
one certificate whose extension repeated a real intermediate's identifier could displace that
intermediate and deny validation of a good chain. So the certificates whose *computed* identifier matches
come first in the returned array, ahead of those that only claim the value — a caller that takes the
first match takes the one that actually holds the key.

## CertificateChain

```php
use SpomkyLabs\Pki\X509\Certificate\CertificateChain;

$chain = CertificateChain::create($leaf, $intermediate, $root);
$chain = CertificateChain::fromPEMs(...$pems);
$chain = CertificateChain::fromPEMString($pemText);

$chain->endEntityCertificate();     // the first
$chain->trustAnchorCertificate();   // the last
$chain->certificates();             // Certificate[], end entity first
count($chain);
echo $chain->toPEMString();
```

The order is **end entity first, trust anchor last** — the order TLS puts a chain on the wire. Both
accessors throw `LogicException` on an empty chain.

!!! warning "`trustAnchorCertificate()` names a position, not a decision"

    It returns the last certificate of the chain, which on a chain from a peer is a certificate the peer
    chose. It is not a trust anchor in any sense that matters. Hence:

    ```php
    $path = $chain->certificationPath();           // or CertificationPath::fromCertificateChain($chain)
    $path->validate($config);                      // throws: no trust anchor
    $path->validate($config->withTrustAnchor($yourRoot));   // this is the question
    ```

    A path built from a peer-supplied chain refuses to validate without an explicit anchor, by design.

## From one to the other

```php
$path = $chain->certificationPath();   // a CertificationPath, reversed: anchor first
```

A `CertificationPath` runs the other way round — trust anchor first, target last — because that is the
order RFC 5280's algorithm walks. The conversion reverses for you.

## Building a trust store

```php
use SpomkyLabs\Pki\CryptoEncoding\PEMBundle;
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;

$trustAnchors = CertificateBundle::fromPEMBundle(PEMBundle::fromFile('/etc/ssl/certs/ca-certificates.crt'));
```

The library reads no system trust store of its own: there is no default list, and no discovery. Point it
at a file your deployment controls, or assemble the bundle from the roots your application ships.

Count what a peer sends before you walk it; see
[Decoding untrusted input](../asn1/untrusted-input.md#what-you-have-to-bound).
