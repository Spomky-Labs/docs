---
description: 'What a certification path is, which way round it runs, and the two halves of the problem: building and validating.'
---

# Certification paths

A certification path is a sequence of certificates running **from a trust anchor to a target**, each one
signed by the one before it.

```
CertificationPath
  [0] the trust anchor         a certificate YOU chose
  [1] an intermediate
  [2] …
  [n] the target              the end-entity certificate you are asking about
```

Note the direction. A TLS chain on the wire runs the other way — end entity first — which is what
[`CertificateChain`](../certificates/bundles-and-chains.md) models. A `CertificationPath` is reversed
because that is the order RFC 5280's algorithm walks.

## Two halves of the problem

**Building** is finding a path: given a target and a bundle of certificates you trust, work out a
sequence that leads from one to the other. See [Building a path](building-a-path.md).

**Validating** is checking it: signatures, dates, constraints, policies. See
[Validating a path](validating-a-path.md).

Building a path does not validate it, and validating one does not require you to have built it. The usual
code does both, in that order:

```php
use SpomkyLabs\Pki\X509\Certificate\CertificateBundle;
use SpomkyLabs\Pki\X509\CertificationPath\CertificationPath;
use SpomkyLabs\Pki\X509\CertificationPath\Exception\PathValidationException;
use SpomkyLabs\Pki\X509\CertificationPath\PathValidation\PathValidationConfig;

$trustAnchors = CertificateBundle::create($rootA, $rootB);              // your trust store
$intermediates = CertificateBundle::create(...$chainFromPeer);          // untrusted, bridges the path

$path = CertificationPath::toTarget($leafFromPeer, $trustAnchors, $intermediates);

try {
    $result = $path->validate(PathValidationConfig::defaultConfig());
} catch (PathValidationException $e) {
    // the chain does not lead to any certificate you trust
}
```

That is the shape to copy. `toTarget()` starts from the trust list you gave it, so the path it returns is
already headed by a certificate you chose.

## The four ways to get a path

| Factory | Head of the path | Needs an explicit anchor to validate? |
|---|---|---|
| `toTarget($target, $trustAnchors, $intermediates)` | from your trust list | no |
| `fromTrustAnchorToTarget($anchor, $target, $intermediates)` | the anchor you named | no |
| `create(...$certificates)` | whatever you passed first | **yes in practice** — a deprecation notice without one |
| `fromCertificateChain($chain)` | whatever the peer sent first | **yes** — throws without one |

`create()` is the constructor an integrator reaches for first, and it is the one that cannot tell a path
anchored in your trust store from one anchored in an attacker's. Prefer `toTarget()`.

## Reading a path

```php
$path->certificates();              // Certificate[], anchor first
$path->trustAnchorCertificate();    // the first
$path->endEntityCertificate();      // the last
$path->certificateChain();          // a CertificateChain, reversed
$path->startsWith($rootA);          // does it begin with these certificates?
count($path);

foreach ($path as $certificate) {
}
```

`startsWith()` is the cheap check that a path begins where you expect — useful when you hold several
anchors and want to know which one a built path used.

## What to read next

- [Building a path](building-a-path.md) — how an issuer is found, and the bounds on the search.
- [Validating a path](validating-a-path.md) — the algorithm, the result, the exceptions.
- [Configuration](configuration.md) — every knob of `PathValidationConfig`, and the ones to turn.
- [What validation does not do](what-validation-does-not-do.md) — **read this before you rely on a
  successful validation.**
