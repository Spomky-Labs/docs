---
description: 'The two RFC 9052 §3.1 checks the library leaves to the caller: alg and crit.'
---

# What the application must check

!!! warning

    The library verifies signatures; it does not decide what a message is allowed to say. Two checks
    [RFC 9052 §3.1](https://datatracker.ietf.org/doc/html/rfc9052#section-3.1) requires are therefore the caller's, and
    both are in the snippet above:

    - **`alg` (label 1)**: "This header parameter MUST be authenticated where the ability to do so exists". Read it
      from the *protected* header, which the signature covers, and compare it with the algorithm you decided to accept
      for that key. A verifier that hard-codes its algorithm and ignores the header still accepts a message that
      announces a different one.
    - **`crit` (label 2)**: it lists the protected header parameters a recipient is *required* to understand. Any
      label in that list your application does not process makes the message unusable: reject it instead of verifying
      it.

When the algorithm is chosen from the message rather than pinned (`Manager::get()` on the `alg` read from the
header), a key that carries its own `alg` and `key_ops` can refuse a downgrade on its own, see
[Key restrictions](../keys/key-restrictions.md).
