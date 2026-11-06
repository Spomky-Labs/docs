---
description: What a successful path validation does not tell you, and the checks your application still owes.
---

# What validation does not do

A successful `validate()` is a precise statement: *this chain is well-formed, every signature holds,
every certificate was in date at the reference instant, the constraints along the path are satisfied, and
it leads to the anchor you named.*

That is less than "this certificate is good". The gap is this page.

## Revocation is not checked

**A revoked certificate validates.** The library has no CRL parser and no OCSP client, and it never opens
a network connection — nothing is fetched from an `authorityInformationAccess` extension or a CRL
distribution point.

This is by design, not an omission waiting for a release. Revocation checking is the calling
application's responsibility.

What the library gives you to do it with:

```php
$extensions = $certificate->tbsCertificate()->extensions();

if ($extensions->hasCRLDistributionPoints()) {
    foreach ($extensions->crlDistributionPoints()->distributionPoints() as $point) {
        // the URIs are in $point->fullName(), fetch and check them yourself
    }
}

if ($extensions->has(Extension::OID_AUTHORITY_INFORMATION_ACCESS)) {
    // AuthorityAccessDescription::OID_METHOD_OSCP gives the responder's URI
}
```

And what identifies a certificate to a CRL: the **(issuer, serial number)** pair.

```php
$tbs = $certificate->tbsCertificate();
$key = [$tbs->issuer()->toString(), $tbs->serialNumber()];
```

The serial number is a decimal string. Comparing serial numbers as PHP integers is how revocation
lookups silently stop matching.

## No hostname, no identity matching

Path validation never looks at a hostname. It does not know you dialled `example.com`.

```php
$names = $certificate->tbsCertificate()->extensions()->subjectAlternativeName()->names();
$names->firstDNS();   // what the issuer wrote
```

Deciding whether that names the server you meant to reach — wildcards, trailing dots, internationalised
domains, whether to look at the common name at all, the rules of the protocol you are speaking — is a
step of your own. The same goes for matching an email address in an S/MIME certificate, or a user
identifier in a client certificate.

## Extended key usage is not checked

RFC 5280's algorithm says nothing about `extKeyUsage`, so neither does the validator. A certificate
issued for email protection validates perfectly well as the far end of a TLS chain.

```php
$extensions = $certificate->tbsCertificate()->extensions();

if (! $extensions->hasExtendedKeyUsage()
    || ! $extensions->extendedKeyUsage()->has(ExtendedKeyUsageExtension::OID_SERVER_AUTH)) {
    throw new RuntimeException('Not a TLS server certificate.');
}
```

`keyUsage` on the end-entity certificate is likewise yours to check: the validator enforces it on
intermediates — `keyCertSign` — not on the leaf.

## No system trust store

There is no default list of roots, and nothing reads the operating system's. Everything you trust, you
hand over:

```php
$trustAnchors = CertificateBundle::fromPEMBundle(PEMBundle::fromFile('/etc/ssl/certs/ca-certificates.crt'));
```

That is a feature — the trust decision is visible in your code — and it means an empty bundle validates
nothing rather than falling back to something broad.

## Attribute certificates need their authorities named

`ACValidator` does not implement RFC 5755 section 5 check 4 on its own. Without
`ACValidationConfig::withTrustedAttributeAuthorities()`, it accepts whatever end-entity certificate the
issuer path ends in. See
[Validating an attribute certificate](../attribute-certificates/validating-an-attribute-certificate.md).

## RSASSA-PSS is refused, not validated

A PSS-signed certificate is refused when it is **parsed**, so it never reaches validation. If your PKI
uses PSS, this library cannot verify its certificates — and the OID is deliberately absent from the
allowed set so that nothing pretends otherwise.

## EdDSA may fail for the wrong reason

Ed25519 and Ed448 are allowed by default, but verification depends on the extensions loaded. On a runtime
without EdDSA the chain fails closed, and `Failed to verify signature: …` is indistinguishable from a bad
signature. Probe at boot; see [The crypto engine](../keys/the-crypto-engine.md).

## Nothing bounds the input for you

The decoder caps nesting depth. It does not cap the size of the string you hand it, or the number of
certificates in a bundle you walk. See
[Decoding untrusted input](../asn1/untrusted-input.md#what-you-have-to-bound).

## The checklist

For a TLS client, after a successful validation:

- [ ] revocation checked, by CRL or OCSP, with your own code;
- [ ] the hostname matched against `subjectAltName`, with the rules of your protocol;
- [ ] `extKeyUsage` includes the purpose you are about to use the certificate for;
- [ ] `keyUsage` on the leaf permits what you are about to do;
- [ ] the configuration was [hardened](configuration.md#what-a-hardened-configuration-looks-like) if your
      deployment can refuse SHA-1 and 1024-bit RSA;
- [ ] the trust anchor came from your trust store, not from the path.

If you are implementing TLS itself, note that the protocol has more requirements than RFC 5280 does. This
library gives you the certificate layer; it is not a TLS stack.
