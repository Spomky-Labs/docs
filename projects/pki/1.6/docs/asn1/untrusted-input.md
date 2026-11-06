---
description: The limits to set before you decode DER a stranger sent, and what the library bounds for you.
---

# Decoding untrusted input

A certificate chain arrives from a peer. A certification request arrives from a form. A DER string is a
recursive, self-describing format, and decoding one is work an attacker gets to choose the shape of.

This page is what to set before you decode material you did not produce. The
[security recommendations](../introduction/security-recommendations.md) list the rest.

## What the library bounds for you

**Nesting depth.** Decoding a constructed type recurses, so an attacker who sends a thousand nested
`SEQUENCE` headers in a few kilobytes would exhaust the stack. The decoder counts levels and refuses
beyond `Element::DEFAULT_MAX_NESTING_DEPTH`, which is 64. Every decoded element takes a level, the
end-of-contents marker of an indefinite length encoding included.

```php
use SpomkyLabs\Pki\ASN1\Element;

Element::maxNestingDepth();      // 64
Element::setMaxNestingDepth(16); // a real X.509 structure rarely nests deeper than ten
```

!!! warning "The cap is global process state"

    `setMaxNestingDepth()` is static and affects every later decode in the process, including the ones
    inside the X.509 layer. Set it once at boot. Set it too low and legitimate material stops decoding.

**Exception type.** Nothing but `DecodeException` escapes `Element::fromDER()`. The type-specific
decoders reach into large-number arithmetic, into constructors and into string validation, any of which
may signal malformed input in its own way; the exception is normalised on the way out, with the original
kept as its previous. So one `catch` is enough:

```php
use SpomkyLabs\Pki\ASN1\Exception\DecodeException;

try {
    $certificate = Certificate::fromDER($bytes);
} catch (DecodeException $e) {
    // malformed; $e->getPrevious() says what the decoder tripped on
}
```

**Repeated optional fields.** The X.509 decoders call `assertUniqueTaggedElements()` before they read
optional fields, so a structure carrying the same tag twice is refused rather than read as its last
copy. See [Tagging](tagging.md#reading-an-optional-field).

**Encodings that are not DER.** A type X.690 only ever allows in primitive form is refused in
constructed form, a `SET OF` must be sorted, and a string type refuses a value outside its character
set.

## What you have to bound

**Size.** The library decodes the string you hand it; it does not know where the string came from. A
hundred megabytes of valid, deeply fanned-out DER is a hundred megabytes of PHP objects. Cap the length
before you decode:

```php
if (strlen($bytes) > 64 * 1024) {
    throw new RuntimeException('Certificate material too large.');
}
```

A certificate is a few kilobytes. A chain is a few more. Pick a limit from what your protocol actually
carries, not from what might fit.

**Count.** A PEM bundle holds as many blocks as the file has. Reading one from a peer means reading
whatever number they chose:

```php
use SpomkyLabs\Pki\CryptoEncoding\PEMBundle;

$bundle = PEMBundle::fromString($chainFromPeer);

if (count($bundle) > 10) {
    throw new RuntimeException('Too many certificates in the chain.');
}
```

**Time.** Path validation walks a policy tree whose size depends on the certificates in the path.
`PathValidationConfig::withMaxLength()` bounds the path — the default is 3 — and bounding the input
bounds the rest. See [Configuration](../certification-paths/configuration.md).

## What decoding does not tell you

Decoding says the bytes are well-formed. It says nothing about whether the structure means anything:

- a certificate that decodes may be expired, revoked, self-signed by a stranger, or signed with an
  algorithm you do not accept;
- a certification request that decodes may carry a signature that does not verify —
  [`verify()` is a separate call](../certification-requests/README.md#verifying-a-request);
- a chain that decodes may lead nowhere you trust.

Decode, then validate. The two are different steps and the library keeps them apart on purpose.
