# What OTPHP is

A one-time password is a short number derived from a secret shared between your server and the user's
device, and from something that changes: the time, or a counter. Both sides compute the same number from
the same inputs, so the user proves they hold the secret without sending it.

OTPHP is the PHP implementation of that computation, in both of its standard forms.

| Specification | Algorithm | What changes |
|---|---|---|
| [RFC 4226](https://datatracker.ietf.org/doc/html/rfc4226) | HOTP | A counter, incremented at each use |
| [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238) | TOTP | The time, in slices of a fixed period |

The provisioning URI, the `otpauth://` address a QR code carries, follows the
[Key Uri Format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format) Google Authenticator
defined and the other applications adopted.

## The public surface

It is small on purpose. Four classes you will name, with an interface each, in the `OTPHP` namespace —
plus the exceptions of `OTPHP\Exception`, and `InternalClock` and `Url`, which are marked `@internal`
and are not yours to use.

| Class | What it is |
|---|---|
| `TOTP` | A time-based password. Holds a PSR-20 clock |
| `HOTP` | A counter-based password |
| `Factory` | Reads an `otpauth://` URI back into a `TOTP` or a `HOTP` |
| `OTP` | The shared, abstract parent. Holds the parameters and the RFC 4226 truncation |

`TOTPInterface` and `HOTPInterface` both extend `OTPInterface`; `Factory` implements `FactoryInterface`.
Type your own services against the interfaces: they are what the library promises not to break inside a
major version.

## Which inputs matter

An OTP object is a bag of parameters, and the password it produces depends on all of them. Two objects
with the same secret and different digests produce different codes, and a user whose application was
configured with one cannot authenticate against the other. The parameters are listed in
[The parameters](../the-parameters/the-parameters.md); the consequence is in
[What to store](../in-your-application/what-to-store.md).

## What it leaves to you

OTPHP verifies a code against a secret. Everything that makes that verification mean something lives in
your application:

* **Storage.** The secret is a credential. Where it goes and how it is protected is your decision.
* **Replay.** A TOTP stays valid for its whole period. Nothing here remembers that a code was already
  accepted thirty seconds ago.
* **Rate limiting.** Six digits are a million possibilities, which is not many. Unlimited attempts defeat
  the factor entirely.
* **Enrolment and recovery.** Showing a QR code, confirming the first code, issuing recovery codes,
  letting a user remove the factor.

[Security recommendations](security-recommendations.md) covers each of these.
