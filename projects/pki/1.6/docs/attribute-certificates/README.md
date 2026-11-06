---
description: 'Attribute certificates after RFC 5755: what they carry, who holds them, and how they differ from public key certificates.'
---

# Attribute certificates

A public key certificate says *this key belongs to this subject*. An attribute certificate says
*this subject has these attributes* — a role, a group, a clearance — and it carries **no key of its own**.

It is an authorisation statement bound to an identity someone else already certified.
[RFC 5755](https://tools.ietf.org/html/rfc5755) defines them.

```
AttributeCertificate
├── AttributeCertificateInfo    holder, issuer, validity, the attributes, extensions
├── AlgorithmIdentifier
└── Signature
```

Same split as everywhere: `AttributeCertificateInfo` builds, `AttributeCertificate` is signed.

## Reading one

```php
use SpomkyLabs\Pki\CryptoEncoding\PEM;
use SpomkyLabs\Pki\X509\AttributeCertificate\AttributeCertificate;

$ac = AttributeCertificate::fromPEM(PEM::fromFile('role.ac'));   // label: ATTRIBUTE CERTIFICATE

$acinfo = $ac->acinfo();
$acinfo->holder();
$acinfo->issuer();
$acinfo->serialNumber();
$acinfo->validityPeriod()->notBeforeTime();
$acinfo->attributes();
$acinfo->extensions();
```

## The holder

The holder is not a name but a reference to a public key certificate, by any of three routes:

```php
$holder = $acinfo->holder();

$holder->hasBaseCertificateID();   // the (issuer, serial) of the holder's certificate
$holder->baseCertificateID();
$holder->hasEntityName();          // a GeneralNames
$holder->entityName();
$holder->hasObjectDigestInfo();    // a digest of the object held
$holder->objectDigestInfo();
```

And the question you actually want:

```php
$ac->isHeldBy($holderCertificate);   // does this AC belong to that certificate?
$ac->isIssuedBy($issuerCertificate);
```

## The issuer

An attribute authority, identified by its own public key certificate:

```php
use SpomkyLabs\Pki\X509\AttributeCertificate\AttCertIssuer;

AttCertIssuer::fromPKC($authorityCertificate);   // what you want
AttCertIssuer::fromName($name);                  // the v1 form, by name alone
```

!!! note "An attribute authority is not a CA"

    Validation refuses an issuer certificate whose `basicConstraints` says `cA:TRUE`. An attribute
    authority signs attribute certificates; it does not issue public key certificates. Its `keyUsage`, if
    it has one, must permit `digitalSignature` or `nonRepudiation` — RFC 5755 section 4.5 accepts either.

## The attributes

`Attributes` here is a `SequenceOfAttributes` with shortcuts for the attributes RFC 5755 defines:

```php
$attributes = $acinfo->attributes();

$attributes->hasRole();
$attributes->role();                       // a RoleAttributeValue
$attributes->roles();                      // all of them
$attributes->hasGroup();
$attributes->group();
$attributes->hasAccessIdentity();
$attributes->hasChargingIdentity();
$attributes->hasAuthenticationInformation();
```

| Class, under `AttributeCertificate\Attribute` | Carries |
|---|---|
| `RoleAttributeValue` | a role name, and optionally the authority that defines it |
| `GroupAttributeValue` | group membership |
| `AccessIdentityAttributeValue` | an identity for access control |
| `ChargingIdentityAttributeValue` | an identity for billing |
| `AuthenticationInfoAttributeValue` | authentication information |

The last three share the `SvceAuthInfo` syntax — a service, an identity and optional auth info. The first
two use the IETF attribute syntax, `IetfAttrSyntax`, whose values are `IetfAttrValue`: an octet string,
an OID or a UTF-8 string, which `isOctets()`, `isOID()` and `isString()` tell apart.

```php
use SpomkyLabs\Pki\X509\AttributeCertificate\Attribute\RoleAttributeValue;
use SpomkyLabs\Pki\X509\GeneralName\UniformResourceIdentifier;

$role = RoleAttributeValue::create(UniformResourceIdentifier::create('urn:roles:administrator'));
$role->roleName();
$role->hasRoleAuthority();
```

## Extensions

The same `Extensions` as a certificate, with two that matter here:

- `TargetInformationExtension` — the servers or services this AC is meant for. Validation checks it
  against the targets you configured;
- `NoRevocationAvailableExtension` — this AC is not revocable.

A **critical** extension the validator does not process makes validation fail, as RFC 5755 section 5
check 7 requires: an attribute certificate carries authorisation, and a critical extension is how its
issuer narrows that authorisation. Accepting one that cannot be processed would grant the attributes
unconditionally. The validator processes exactly those two; declare any others with
`ACValidationConfig::withAdditionalCriticalExtensions()`.

## Verifying and validating

```php
$ac->verify($authorityPublicKeyInfo);   // the signature alone
```

As with certificates, that is one fact and not an authorisation decision. Validating an attribute
certificate means validating **two certification paths** — the holder's and the issuer's — and more. See
[Validating an attribute certificate](validating-an-attribute-certificate.md).

## In and out

```php
AttributeCertificate::fromPEM($pem);
AttributeCertificate::fromDER($der);
AttributeCertificate::fromASN1($sequence);

$ac->toPEM()->string();
$ac->toDER();
echo $ac;
```

## What to read next

- [Issuing an attribute certificate](issuing-an-attribute-certificate.md)
- [Validating an attribute certificate](validating-an-attribute-certificate.md) — including the check
  the validator does not make for you.
