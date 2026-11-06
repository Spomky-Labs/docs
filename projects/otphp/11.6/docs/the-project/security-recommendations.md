# Security recommendations

OTPHP decides whether a code matches a secret. Whether that answer protects an account depends on the
things around it, and those are yours to build. This page is the list of them.

## Treat the secret as a credential

A one-time password secret is not a password hash. It is a *shared* secret: whoever reads it can produce
valid codes forever, silently, from anywhere. A leaked OTP table is a leaked second factor for every
account in it.

* Encrypt it at rest, with a key held outside the database.
* Never log it, and never put it in an error message, a stack trace or a bug report. The provisioning URI
  contains it in full.
* Never send it to a third party. That includes the online QR code generators; see
  [QR codes](../configuring-an-application/qr-codes.md).
* Generate one per account, from the library. `TOTP::generate()` uses `random_bytes()`; nothing else is
  acceptable as a source.

## Rate-limit verification

Six digits are one million values, and a TOTP accepts a whole period's worth of guesses. Without a limit,
an attacker who holds the password walks through the second factor in hours.

Count failures per account, not per IP address, and lock the factor after a handful. A lockout that the
user can lift by signing in again is enough; a silent counter that never trips is not.

## Refuse a code twice

The library has no memory. A TOTP it accepted at second 1 of a period it will accept again at second 29,
which is long enough for a code read over someone's shoulder, or captured by a phishing page, to be
replayed.

Store the last accepted timecode — or the last accepted code — with the account, and refuse anything that
is not newer.

For HOTP the library does keep the counter moving: `verify()` increments it on success, so the same code
cannot be used twice against the same object. That only holds if you **persist the counter after every
successful verification**. See [The counter](../the-parameters/the-counter.md).

## Keep the window small

The window exists because clocks drift, not because users are slow. Every second of window is another
code an attacker may guess with.

A window of a few seconds covers a phone whose clock is slightly off. A window close to the period
roughly triples the codes you accept. See [The window](../one-time-passwords/the-window.md).

## Choose the parameters once, and record them

Use `sha1`, `sha256` or `sha512`; they are the only digests the specifications define and the only ones
authenticator applications read. `SHA-2` is preferable. Digests shorter than 19 bytes are rejected
outright — the RFC 4226 truncation cannot work with them — and that rejection is a real defence, not a
formality. See [The digest and the digits](../the-parameters/the-digest-and-the-digits.md).

Six digits and a thirty-second period are what every application expects. Eight digits are fine if your
users' application supports them, and nothing else is worth the interoperability it costs.

Whatever you choose, store it alongside the secret, or store the whole provisioning URI. A parameter you
change later invalidates every account provisioned with the old one. See
[What to store](../in-your-application/what-to-store.md).

## Confirm enrolment

Ask the user for one valid code before you turn the factor on. A QR code that was scanned by nothing, or
by an application whose clock is wrong, otherwise locks the account at the next sign-in.

Issue recovery codes at the same time, and treat them like passwords: hashed, single-use, countable.

## Serve the enrolment page over HTTPS, and only to the owner

The QR code is the secret, rendered. Show it once, to an authenticated session, over TLS, and do not let
it be fetched again afterwards. Caches, proxies and browser history are all places it should not land.

## Reporting a vulnerability

Security issues in OTPHP go to `security@spomky-labs.com`, never to the public issue tracker. The process,
and the versions that receive fixes, are in
[SECURITY.md](https://github.com/Spomky-Labs/otphp/blob/HEAD/SECURITY.md).
