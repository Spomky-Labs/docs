---
title: OTPHP
description: The published security advisories of OTPHP, their severity and the versions that fix each one.
---

# OTPHP

The published advisories of [Spomky-Labs/otphp](https://github.com/Spomky-Labs/otphp/security/advisories), the newest first.
Each one names the packages and the version ranges it affects. The latest release of every supported
line carries every fix.

| Published | Advisory | Severity | Fixed in |
|---|---|---|---|
| 2026-11-07 | [Label validation accepts an encoded colon at the start of the account name](https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-h38w-h2gf-6qv2) | Low | 11.4.4, 11.5.1 |
| 2026-11-07 | [TOTP::expiresIn() throws an uncaught TypeError for a provisioning URI with a future epoch and a very large period](https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-4v5c-4hwq-6f6m) | Medium | 11.4.4, 11.5.1 |
| 2026-11-07 | [Unbounded counter parameter in a provisioning URI triggers an uncaught TypeError in HOTP verification](https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-526c-px8p-72x8) | Medium | 11.4.4, 11.5.1 |
| 2026-05-31 | [Mass-assignment in Factory::loadFromProvisioningUri lets a hostile provisioning URI corrupt OTP state or leak an uncaught TypeError](https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-2jx3-65f3-xr8r) | Medium | 11.4.3 |
| 2026-05-31 | [Unbounded digits parameter in a provisioning URI triggers an uncaught DivisionByZeroError in OTP generation](https://github.com/Spomky-Labs/otphp/security/advisories/GHSA-g7m4-839x-ch6v) | Medium | 11.4.3 |
