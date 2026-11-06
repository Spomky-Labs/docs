---
description: Implicit and explicit tags, the four tag classes, and how to read an optional field of a certificate.
---

# Tagging

A `SEQUENCE` whose fields are optional needs a way to tell them apart, and ASN.1 does it with tags. Half
the fields of an X.509 structure are tagged, so reading one by hand means knowing which kind of tag it
carries.

## Explicit and implicit

An **explicit** tag wraps the value: the tag is added around an encoding that still says what the value
is. An **implicit** tag replaces the value's own tag: nothing in the bytes says what is inside, so the
reader has to know from the specification.

```php
use SpomkyLabs\Pki\ASN1\Type\Primitive\Integer;
use SpomkyLabs\Pki\ASN1\Type\Tagged\ExplicitlyTaggedType;
use SpomkyLabs\Pki\ASN1\Type\Tagged\ImplicitlyTaggedType;

$explicit = ExplicitlyTaggedType::create(0, Integer::create(42));
$implicit = ImplicitlyTaggedType::create(1, Integer::create(42));
```

Reading one back, you say which it is and — for an implicit tag — what is inside:

```php
use SpomkyLabs\Pki\ASN1\Element;

$tagged = $element->expectTagged(0);          // a tagged type, tag 0
$value = $tagged->asExplicit()->asInteger();  // unwrap, then assert the type

$tagged = $element->expectTagged(1);
$value = $tagged->asImplicit(Element::TYPE_INTEGER)->asInteger();
```

`asExplicit()` and `asImplicit()` return an `UnspecifiedType`, so the `as*()` chain continues. The
`expect*` variants — `expectExplicit()`, `expectImplicit()` — return the tagging interface itself when
you want to work with it rather than with the value.

!!! warning "An implicit tag read as explicit decodes garbage, not an error"

    The bytes inside an implicitly tagged element are the content of the value, with no identifier of
    their own. Reading them as if they were a complete element may well succeed and give you something
    unrelated. The specification says which kind of tag a field carries; follow it.

## The tag classes

| Class | Constant | Where you meet it |
|---|---|---|
| Universal | `Identifier::CLASS_UNIVERSAL` | the built-in types: `INTEGER`, `SEQUENCE`, … |
| Context-specific | `Identifier::CLASS_CONTEXT_SPECIFIC` | the optional fields of almost every X.509 structure |
| Application | `Identifier::CLASS_APPLICATION` | rare; some older PKCS structures |
| Private | `Identifier::CLASS_PRIVATE` | never, unless your own schema uses it |

Context-specific is the default of `ExplicitlyTaggedType::create()` and
`ImplicitlyTaggedType::create()`, which is why the examples above pass only a number. The other classes
have their own wrappers, `ApplicationType` and `PrivateType`, reached with `asApplication()` and
`asPrivate()`.

```php
$element->typeClass() === Identifier::CLASS_CONTEXT_SPECIFIC;
```

## Reading an optional field

`Structure::hasTagged()` and `getTagged()` find a field by its tag:

```php
if ($sequence->hasTagged(3)) {
    $extensions = $sequence->getTagged(3)->asExplicit()->asSequence();
}
```

!!! note "A repeated tag is not a field"

    The optional fields of a structure are distinct, so the same tag twice is not a field but a second
    copy of one. `hasTagged()` keeps only the last and would silently drop what came before, which is why
    the X.509 decoders of this library call `assertUniqueTaggedElements()` first. Do the same when you
    decode a structure whose fields must each appear once:

    ```php
    $sequence->assertUniqueTaggedElements('TBSCertificate');
    ```

    The string names the structure in the exception message.

## A worked example

`TBSCertificate` holds its extensions in field `[3]`, explicitly tagged. Reading them without the X.509
layer:

```php
use SpomkyLabs\Pki\ASN1\Type\Constructed\Sequence;
use SpomkyLabs\Pki\X509\Certificate\Extensions;

$certificate = Sequence::fromDER($der);           // Certificate
$tbs = $certificate->at(0)->asSequence();         // TBSCertificate
$tbs->assertUniqueTaggedElements('TBSCertificate');

$extensions = $tbs->hasTagged(3)
    ? Extensions::fromASN1($tbs->getTagged(3)->asExplicit()->asSequence())
    : Extensions::create();
```

In practice, `Certificate::fromDER($der)->tbsCertificate()->extensions()` is that, already done and
checked. Go down to this level for a structure the library does not model.
