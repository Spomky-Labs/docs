---
description: Why two certificates can name the same party with different bytes, and what Name::equals() does about it.
---

# Comparing names

Two certificates can name the same party with different bytes. One writes the common name as a
`PrintableString`, the other as a `BMPString`; one writes `ACME Ltd`, the other `acme  ltd`. Path
validation has to chain an issuer DN to a subject DN across that, so comparison is a specified
algorithm, not a string comparison.

```php
$subject->equals($issuer);   // what you want
$subject->toString() === $issuer->toString();   // what you do not
```

## What `equals()` does

Three levels, following RFC 5280 section 7.1.

**A `Name`** is equal to another when they have the same number of RDNs and each RDN is equal to the one
at its position.

**An `RDN`** is a `SET`, so two of them are equal when their attributes match as a multiset, in any
order. Order is not part of the meaning.

**An `AttributeTypeAndValue`** is equal to another when the type OIDs match and the two values compare
equal under their matching rules — each value prepared under **its own** syntax.

!!! note "Each side is prepared under its own rule"

    Taking the matching rule from one side alone would push the other side's octets through the wrong
    transcoder, and then the same name written as a `BMPString` and as a `PrintableString` would compare
    as two different names. That is not a cosmetic bug: it means a `directoryName` a name constraint
    excludes becomes reachable by re-encoding it. Both sides are prepared under their own syntax, which
    is why `equals()` is the only comparison worth trusting.

## The matching rules

An attribute value chooses its rule in `equalityMatchingRule()`.

| Rule | Compares |
|---|---|
| `CaseIgnoreMatch` | after string preparation, case-folded. The rule of every directory string |
| `CaseExactMatch` | after string preparation, case kept |
| `BinaryMatch` | octet by octet, no preparation |

`StringPrepMatchingRule` is the base of the first two, and `prepare()` on it gives the prepared form of a
value — useful when you want to index names, or to see why two values you expected to match do not:

```php
use SpomkyLabs\Pki\X501\MatchingRule\CaseIgnoreMatch;
use SpomkyLabs\Pki\ASN1\Element;

$rule = CaseIgnoreMatch::create(Element::TYPE_UTF8_STRING);

$rule->prepare('  ACME   Ltd  ');       // "acme ltd"
$rule->compare('ACME Ltd', 'acme  ltd'); // true
```

## String preparation

`StringPreparer` is the X.520 and RFC 4518 pipeline, in six steps:

| Step | Does |
|---|---|
| `STEP_TRANSCODE` | the string type's encoding to UTF-8 |
| `STEP_MAP` | case folding, and mapping the characters that map to nothing |
| `STEP_NORMALIZE` | Unicode normalisation |
| `STEP_PROHIBIT` | refuse the characters the specification forbids |
| `STEP_CHECK_BIDI` | refuse a string that mixes directions illegally |
| `STEP_INSIGNIFICANT_CHARS` | collapse the runs of space that carry no meaning |

```php
use SpomkyLabs\Pki\X501\StringPrep\StringPreparer;
use SpomkyLabs\Pki\ASN1\Element;

$preparer = StringPreparer::forStringType(Element::TYPE_UTF8_STRING)->withCaseFolding(true);
$prepared = $preparer->prepare($value);
```

A string the prohibit or bidi step refuses raises `StringPreparationException`. Preparation is where
`mbstring` is required: this is the step that needs it.

## The cost of comparing

A multi-valued RDN makes the multiset question real, and pairing the two sides off one at a time costs a
comparison for every pair — work quadratic in the number of attributes, each step preparing a string
afresh. An RDN whose attributes an attacker put in the reverse order would make you pay for it.

So where the matching rules can name their values, the attributes are grouped by that name and the answer
takes one pass. `AttributeTypeAndValue::comparisonKey()` is that name: the type OID, the rule class and
the prepared value, or `null` for a rule that cannot produce one. Two attributes are equal exactly when
their keys are identical.

You can use it yourself to index names — as a hash map key, or a database column — rather than comparing
every pair:

```php
$key = $attributeTypeAndValue->comparisonKey();   // string, or null
```

## Comparing certificates, not names

The questions above are about names. For certificates:

```php
$a->equals($b);                     // the two encodings, octet by octet
$a->hasEqualSubjectIdentity($b);    // same subject, same key, same serial number
```

!!! warning "`hasEqualSubjectIdentity()` is not an identity check"

    Two certificates can agree on subject, key and serial number and still be issued by different
    issuers with different extensions. It answers a narrow question; do not use it to decide that two
    certificates are interchangeable.

`CertificateBundle::contains()` is built on `equals()`, so a trust store lookup is an exact-encoding
lookup. See [Bundles and chains](../certificates/bundles-and-chains.md).
