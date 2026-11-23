---
title: WebAuthn Framework
description: The published security advisories of WebAuthn Framework, their severity and the versions that fix each one.
---

# WebAuthn Framework

The published advisories of [web-auth/webauthn-framework](https://github.com/web-auth/webauthn-framework/security/advisories), the newest first.
Each one names the packages and the version ranges it affects. The latest release of every supported
line carries every fix.

| Published | Advisory | Severity | Fixed in |
|---|---|---|---|
| 2026-11-19 | [Default client override policy lets the client waive the attestation that a creation profile requests](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-473f-pfcw-p4h2) | Medium | 5.3.13 |
| 2026-11-19 | [CheckMetadataStatement skips the attestation trust path verification under the null AAGUID](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-2jv3-c2vg-rhc4) | Medium | 5.3.13 |
| 2026-11-19 | [webauthn-stimulus registration and authentication controllers send the PRF extension results to the server](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-79w9-wmw2-9hh3) | Medium | 5.3.15 |
| 2026-11-19 | [Client override of authenticatorAttachment or residentKey resets the user verification of a creation profile to preferred](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-2989-5cjp-qc2p) | Low | 5.3.15 |
| 2026-11-17 | [Symfony bundle: user verification bypass with a challenge issued by another endpoint](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-g9ff-w9h6-7ff3) | Low | 5.3.13 |
| 2026-11-17 | [RequestBodyUserEntityGuesser lets users add passkeys to other accounts](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-3chw-82qh-p72w) | High | 5.3.13 |
| 2026-11-17 | [StringStream::read() allocates the length declared by CBOR data before checking it (denial of service)](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-rxc4-cg58-jrpw) | Medium | 5.3.13 |
| 2026-11-17 | [Metadata status report check reads a single report and ignores REVOKED](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-p8cj-mmjr-5c2m) | Low | 5.3.13<br>no fix for `web-auth/metadata-service` |
| 2026-11-17 | [WebauthnPassport ignores the firewall's user provider, allowing impersonation](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-4485-9q39-m27g) | High | 5.3.13 |
| 2026-11-17 | [FidoAllianceCompliantMetadataService accepts a metadata BLOB that does not chain to a trust anchor](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-p653-gg6c-rrjw) | Low | 5.3.13<br>no fix for `web-auth/metadata-service` |
| 2026-11-17 | [Assertion options return an empty allowCredentials for accounts without credentials, allowing username enumeration](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-pm4w-cq4x-rv8q) | Medium | 5.3.10 |
| 2026-11-17 | [Attestation certificates sent as PEM text allow forged packed/TPM attestations and an unauthenticated denial of service](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-c9p6-r72h-rp3x) | High | 5.3.13<br>no fix for `web-auth/metadata-service` |
| 2026-11-17 | [SimpleFakeCredentialGenerator decoys can be told apart from real credentials, allowing username enumeration](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-8gvp-8vj9-p3q7) | Medium | 5.3.13 |
| 2026-05-31 | [SimpleFakeCredentialGenerator with an empty secret produces predictable fake credentials, weakening username enumeration protection](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-gq4g-fpc9-vjfq) | Low | 5.3.5 |
| 2026-05-24 | [Sensitive HTTP headers leaked through INFO-level logs in WebauthnAuthenticator](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-q683-8468-r6h6) | Medium | 5.3.4 |
| 2026-05-02 | [User Verification Downgrade via Default-Open ClientOverridePolicy](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-h4fw-6r7f-w494) | Low | 5.3.1 |
| 2026-03-08 | [allowed_origins collapses URL-like origins to host-only values, bypassing exact origin validation](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-f7pm-6hr8-7ggm) | Medium | 5.2.4 |
| 2024-07-14 | [Enumeration of valid usernames](https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-875x-g8p7-5w27) | Medium | 4.9.0 |
