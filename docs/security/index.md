---
title: Security
description: How to report a vulnerability in a library of Slabs, how an application learns that a version it installs is affected, and the advisories of each library.
---

# Security

## Reporting a vulnerability

A security problem is never reported in a public issue, pull request or discussion: that hands it to every
user of the library before a fix exists. Report it privately, either way:

- with the form **Report a vulnerability** of the Security tab of the repository, which opens a private
  thread with the maintainers;
- by email to [security@spomky-labs.com](mailto:security@spomky-labs.com).

The security policy of each repository, `SECURITY.md`, says which release lines receive fixes.

## Knowing that a version is affected

Every advisory is published on the repository of its library, then enters the GitHub Advisory Database and
the advisories that Packagist serves. From there:

- `composer audit` lists the installed packages that an advisory names;
- Composer refuses such a version on `composer update` and `composer require`, by default since
  Composer 2.9;
- Dependabot alerts a repository on GitHub whose lock file holds one.

## The advisories of each library

| Library | Package |
|---|---|
| [WebAuthn Framework](webauthn.md) | `web-auth/webauthn-lib` and the packages of its repository |
| [JWT Framework](jwt.md) | `web-token/jwt-library` and the packages of its repository |
| [OTPHP](otphp.md) | `spomky-labs/otphp` |
| [PKI Framework](pki.md) | `spomky-labs/pki-framework` |
| [CBOR PHP](cbor.md) | `spomky-labs/cbor-php` |
| [COSE](cose.md) | `web-auth/cose-lib` |

The other libraries, Access Control Framework, PWA Bundle and Web Push Framework, have no published
advisory.
