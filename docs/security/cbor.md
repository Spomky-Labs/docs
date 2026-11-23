---
title: CBOR PHP
description: The published security advisories of CBOR PHP, their severity and the versions that fix each one.
---

# CBOR PHP

The published advisories of [Spomky-Labs/cbor-php](https://github.com/Spomky-Labs/cbor-php/security/advisories), the newest first.
Each one names the packages and the version ranges it affects. The latest release of every supported
line carries every fix.

| Published | Advisory | Severity | Fixed in |
|---|---|---|---|
| 2026-09-10 | [Denial of service and error-contract escapes when decoding hostile CBOR (quadratic map normalize, tag 4/5 key memory exhaustion, bignum base conversion, ValueError/RuntimeException from decode)](https://github.com/Spomky-Labs/cbor-php/security/advisories/GHSA-jfrf-557c-963v) | High | 3.3.5 |
| 2026-08-31 | [Hostile input raises exceptions outside the documented error contract (64-bit headers, assert() used as validation)](https://github.com/Spomky-Labs/cbor-php/security/advisories/GHSA-pjwm-422x-vvh5) | Medium | 3.3.4 |
| 2026-08-31 | [Map keys are stored as native PHP array offsets, causing an uncaught TypeError and silent key collisions](https://github.com/Spomky-Labs/cbor-php/security/advisories/GHSA-388j-mw2g-rx5f) | Medium | 3.3.4 |
| 2026-08-31 | [Unbounded exponent in BigFloat and DecimalFraction tags allows uncatchable memory exhaustion](https://github.com/Spomky-Labs/cbor-php/security/advisories/GHSA-pf28-pvhp-7mm5) | High | 3.3.4 |
