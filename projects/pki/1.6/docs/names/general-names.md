---
description: The nine choices of GeneralName, what each one holds, and where certificates use them.
---

# General names

A distinguished name is not the only way a certificate names something. `subjectAltName`,
`issuerAltName`, `nameConstraints`, the CRL distribution points and the attribute certificate structures
all use `GeneralName`, a choice of nine.

For a TLS certificate, this is where the hostname actually lives: the common name is a convention the web
PKI abandoned, and `subjectAltName` is normative.

## The nine choices

| Tag | Class, under `X509\GeneralName` | Holds |
|---|---|---|
| `TAG_OTHER_NAME` | `OtherName` | an OID and any element |
| `TAG_RFC822_NAME` | `RFC822Name` | an email address |
| `TAG_DNS_NAME` | `DNSName` | a host name |
| `TAG_X400_ADDRESS` | `X400Address` | an X.400 address, kept as a `Sequence` |
| `TAG_DIRECTORY_NAME` | `DirectoryName` | a `Name` |
| `TAG_EDI_PARTY_NAME` | `EDIPartyName` | an EDI party name, kept as a `Sequence` |
| `TAG_URI` | `UniformResourceIdentifier` | a URI |
| `TAG_IP_ADDRESS` | `IPv4Address`, `IPv6Address` | an address, and in a name constraint a mask |
| `TAG_REGISTERED_ID` | `RegisteredID` | an OID |

## Building them

```php
use SpomkyLabs\Pki\X501\ASN1\Name;
use SpomkyLabs\Pki\X509\GeneralName\DirectoryName;
use SpomkyLabs\Pki\X509\GeneralName\DNSName;
use SpomkyLabs\Pki\X509\GeneralName\GeneralNames;
use SpomkyLabs\Pki\X509\GeneralName\IPv4Address;
use SpomkyLabs\Pki\X509\GeneralName\RFC822Name;
use SpomkyLabs\Pki\X509\GeneralName\UniformResourceIdentifier;

$names = GeneralNames::create(
    DNSName::create('example.com'),
    DNSName::create('www.example.com'),
    RFC822Name::create('admin@example.com'),
    UniformResourceIdentifier::create('https://example.com/'),
    IPv4Address::create('192.0.2.1'),
    DirectoryName::create(Name::fromString('cn=example.com'))
);
```

`X400Address` and `EDIPartyName` take a `Sequence`: the library carries them without modelling their
contents, which nothing in a modern PKI uses.

`OtherName` is the escape hatch — an OID and any element:

```php
use SpomkyLabs\Pki\ASN1\Type\Primitive\UTF8String;
use SpomkyLabs\Pki\X509\GeneralName\OtherName;

$name = OtherName::create('1.3.6.1.4.1.99999.1', UTF8String::create('whatever your schema says'));
```

## Reading them

`GeneralNames` is a collection, with shortcuts for the three types you usually want:

```php
$names = $certificate->tbsCertificate()->extensions()->subjectAlternativeName()->names();

$names->firstDNS();   // the first DNS name, as a string
$names->firstURI();   // the first URI
$names->firstDN();    // the first directory name, as a Name
```

Each throws when there is none of that type. Ask first, or walk the collection:

```php
use SpomkyLabs\Pki\X509\GeneralName\GeneralName;

if ($names->has(GeneralName::TAG_DNS_NAME)) {
    foreach ($names->allOf(GeneralName::TAG_DNS_NAME) as $name) {
        /** @var \SpomkyLabs\Pki\X509\GeneralName\DNSName $name */
        echo $name->name();
    }
}

$names->firstOf(GeneralName::TAG_IP_ADDRESS);
count($names);
```

Every `GeneralName` answers `string()` and `(string)`, so printing one needs no type switch. For the
value in its own shape, the accessor differs by class:

```php
$dnsName->name();
$rfc822Name->email();
$uri->uri();
$directoryName->dn();              // a Name
$registeredID->oid();
$ipAddress->address();
$ipAddress->mask();                // only in a name constraint
$otherName->type();                // the OID
```

## Comparing them

```php
$a->equals($b);
```

Two general names are equal when they are the same choice and their encodings agree, octet for octet.

!!! warning "`GeneralName::equals()` is a byte comparison, including for a directory name"

    It compares the DER of the two choices, so a `DirectoryName` whose `Name` says the same thing in a
    different string type is **not** equal under it. For the semantic question, take the names out and
    use `Name::equals()`:

    ```php
    $a->dn()->equals($b->dn());   // the X.501 rules, see Comparing names
    ```

    Name constraint processing inside path validation already does the right thing: it compares a
    `directoryName` constraint against a subject with the name comparison rules, not with this method.

## Addresses and masks

`IPv4Address` and `IPv6Address` take an optional mask, and the mask is only meaningful in a name
constraint, where the pair describes a subnet:

```php
use SpomkyLabs\Pki\X509\GeneralName\IPv4Address;

IPv4Address::create('192.0.2.1');                     // in a subjectAltName
IPv4Address::create('192.0.2.0', '255.255.255.0');    // in a nameConstraints
```

Calling `mask()` on an address that has none throws `LogicException`.

!!! warning "A hostname in a certificate is not a hostname you matched"

    `firstDNS()` gives you the string the issuer wrote. Deciding whether it names the server you meant to
    reach — wildcards, trailing dots, internationalised domains, the rules of the protocol you are
    speaking — is a step of your own that this library does not perform, and that path validation never
    looks at.
