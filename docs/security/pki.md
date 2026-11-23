---
title: PKI Framework
description: The published security advisories of PKI Framework, their severity and the versions that fix each one.
---

# PKI Framework

The published advisories of [Spomky-Labs/pki-framework](https://github.com/Spomky-Labs/pki-framework/security/advisories), the newest first.
Each one names the packages and the version ranges it affects. The latest release of every supported
line carries every fix.

| Published | Advisory | Severity | Fixed in |
|---|---|---|---|
| 2026-09-08 | [Name constraints are never enforced during certification path validation](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-3p3r-m556-g5px) | Critical | 1.6.2 |
| 2026-09-08 | [Unrecognized critical certificate extensions are silently ignored during path validation](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-v76j-9ghr-85fr) | High | 1.6.2 |
| 2026-09-08 | [TBSCertificate::fromCSR() copies attacker-controlled extensions, allowing a requester to obtain a CA certificate](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-5474-45mw-c3xq) | High | 1.6.2 |
| 2026-09-08 | [Unbounded recursion in the ASN.1/DER decoder causes a stack-exhaustion crash (SIGSEGV)](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-xjj7-24gw-437v) | High | 1.6.2 |
| 2026-09-08 | [Missing loop detection in CertificationPathBuilder allows memory exhaustion with two crafted certificates](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-c67f-8q64-6hxh) | High | 1.6.2 |
| 2026-09-08 | [CertificationPath::validate() silently treats the first certificate of the chain as the trust anchor](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-mxjh-6r54-88x9) | High | 1.6.2 |
| 2026-09-08 | [X.509 v1/v2 certificates are accepted as intermediate CAs without any basicConstraints check](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-vw7q-hxmh-m835) | High | 1.6.2 |
| 2026-09-08 | [Signature is verified over a re-encoded TBSCertificate, making certificates malleable](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-f28f-xc9q-m482) | Medium | 1.6.2 |
| 2026-09-08 | [UTCTime two-digit years 50-69 are decoded with the wrong century, so expired certificates can be seen as valid](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-j49g-8r6c-p7w2) | Low | 1.6.2 |
| 2026-09-08 | [MD4, MD5 and SHA-1 certificate signatures are accepted with no way to restrict the algorithm set](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-5gp6-jr6q-ffx7) | Medium | 1.6.2 |
| 2026-09-08 | [Malformed ASN.1 input raises a TypeError that escapes catch(Exception), crashing the caller](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-jj8p-rwmj-6rjj) | Medium | 1.6.2 |
| 2026-09-08 | [Duplicate certificate extensions are silently merged, last occurrence wins](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-wc4q-rp39-hwpf) | Low | 1.6.2 |
| 2026-09-08 | [No syntax validation on dNSName / rfc822Name allows embedded NUL bytes in subjectAltName](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-6q28-45jq-2628) | Low | 1.6.2 |
| 2026-09-08 | [Certificate serial numbers default to 0 and withRandomSerialNumber() yields under 64 bits of entropy](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-8qrh-8g3j-pxvv) | Low | 1.6.2 |
| 2026-09-08 | [KeyUsage and reasonFlags bits are read from the wrong end of an over-long BIT STRING, so keyCertSign can be forged](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-gjx8-fvx6-qg7q) | High | 1.6.2 |
| 2026-09-08 | [A second [3] extensions element in tbsCertificate silently replaces the first, hiding basicConstraints and keyUsage](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-9hcj-84c7-2pj8) | High | 1.6.2 |
| 2026-09-08 | [Distinguished name comparison is defeated by the ASN.1 string type and by invisible characters, and made to collide by lossy transcoding](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-2rhj-2r69-j232) | High | 1.6.2 |
| 2026-09-08 | [Name constraints are evaded by names the matcher does not canonicalise: a trailing dot, and URIs PHP parses differently from browsers](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-mh5j-7xj5-9h45) | High | 1.6.2 |
| 2026-09-08 | [iPAddress GeneralNames silently encode a different address, turning an IPv6 name constraint into a wildcard IPv4 constraint](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-6chf-2x6r-fjhg) | High | 1.6.2 |
| 2026-09-08 | [The MAX_PATHS bound never fires when no path reaches a trust anchor, so 7 KB of certificates costs minutes of CPU](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-rfxw-c9pp-xvfw) | High | 1.6.2 |
| 2026-09-08 | [A few kilobytes of crafted DER cost minutes of CPU: unbounded quadratic accumulation in tag numbers, OID sub-identifiers and REAL mantissas](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-v473-mx2x-xqpv) | High | 1.6.2 |
| 2026-09-08 | [Attribute certificate signatures are exempt from the configured signature algorithm and RSA key size policy](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-85g4-f9rx-c6ww) | High | 1.6.2 |
| 2026-09-08 | [ECDSA signature values are re-encoded before verification, so one certificate has an unlimited supply of accepted byte encodings](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-mx53-vr97-rxr2) | Medium | 1.6.2 |
| 2026-09-08 | [The certificate policy tree grows multiplicatively per certificate, so a signed chain from a delegated sub-CA exhausts memory](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-34rx-vp5j-q2wr) | Medium | 1.6.2 |
| 2026-09-08 | [An unsupported critical extension in an attribute certificate is ignored, so the issuer's restrictions are silently discarded](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-6pj8-5pjp-gj6w) | Medium | 1.6.2 |
| 2026-09-08 | [PEM_REGEX backtracks cubically, so 4 KB of text costs more CPU than parsing thousands of real certificates](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-x673-qv99-7268) | Medium | 1.6.2 |
| 2026-09-08 | [Comparing a multi-valued RDN re-encodes and re-parses both names, so a 14 KB certificate costs 0.3 s per name comparison](https://github.com/Spomky-Labs/pki-framework/security/advisories/GHSA-894f-9q28-7w2x) | Medium | 1.6.2 |
