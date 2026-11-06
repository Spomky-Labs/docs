---
description: 'COSE_Mac0 and COSE_Mac, and why the tag covers the MAC_structure.'
---

# Message authentication codes

The MAC algorithms, HMAC and AES-CBC-MAC, are listed in [Algorithms](../algorithms/mac-algorithms.md), with the
conditions AES-CBC-MAC comes with; the key they take, and what is checked about it, in
[Validating symmetric keys](../keys/validating-symmetric-keys.md).

- [COSE_Mac0](cose-mac0.md) — a MAC without recipients
- [COSE_Mac](cose-mac.md) — a MAC whose recipients carry the authentication key
- [The tag covers the MAC_structure](the-tag-covers-the-mac-structure.md) — why a tag over the bare
  payload is bound to nothing
