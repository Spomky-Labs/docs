---
description: 'The algorithms that are weak but still required, and the acknowledgement each one asks for.'
---

# Non-standard and insecure algorithms

!!! warning

    **RS1 (SHA-1) is not secure.** SHA-1 is no longer acceptable for digital signatures (see
    [RFC 6194](https://datatracker.ietf.org/doc/html/rfc6194) and NIST SP 800-131A); the algorithm is kept only for
    the legacy authenticators that still rely on it. Creating it emits an `E_USER_WARNING` unless you explicitly
    acknowledge the risk:

    ```php
    use Cose\Algorithm\Signature\RSA\RS1;

    $algorithm = RS1::create(acknowledgeInsecureAlgorithm: true);
    ```

    The same acknowledgement applies to `Algorithms::getOpensslAlgorithmFor()` and `Algorithms::getHashAlgorithmFor()`,
    which hand out the very same primitive without any object being created:

    ```php
    use Cose\Algorithms;

    $digest = Algorithms::getOpensslAlgorithmFor(Algorithms::COSE_ALGORITHM_RS1, acknowledgeInsecureAlgorithm: true);
    ```

    As of the next major version, omitting that acknowledgement will throw an exception instead of warning.

!!! warning

    **`Ed256` (-260) and `Ed512` (-261) are not defined by any specification, and their identifiers are not theirs.**
    Both hash the message and sign the digest with pure **Ed25519**, without the `dom2` prefix that would make it the
    Ed25519ph of [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032) §5.1, whose §8.5 says prehashed variants
    "SHOULD NOT be used" anyway. IANA has since assigned -260 to WalnutDSA
    ([RFC 9021](https://www.rfc-editor.org/rfc/rfc9021)) and -261 to TurboSHAKE128
    ([RFC 9861](https://www.rfc-editor.org/rfc/rfc9861)), so a conforming implementation reads objects produced by these
    classes as those algorithms. Despite its name, `Ed512` is not Ed448 and rejects an Ed448 key; EdDSA with Curve448 is
    `Cose\Algorithm\Signature\FullySpecified\Ed448` (-53).

    No authenticator emits these identifiers. Prefer `Ed25519` (-8 or -19). They are kept for the deployments that
    already use the construction on both ends, and only against an explicit acknowledgement:

    ```php
    use Cose\Algorithm\Signature\EdDSA\Ed256;

    $algorithm = Ed256::create(acknowledgeNonStandardAlgorithm: true);
    ```

    As of the next major version, omitting that acknowledgement will throw an exception, and the identifiers will move
    out of the range IANA administers.
