# Security recommendations

Signed or Encrypted Tokens are not just the next trendy/popular way to authenticate users. They provide great features but when used incorrectly they can expose your application to major security issues.

Please read the following recommendations carefully.

## Algorithms

### Algorithm choice

If all parties are able to protect their keys (e.g. private applications), symmetric algorithms are a good choice as they are faster in general. If you use public clients, you should prefer asymmetric algorithms.

### Available algorithms

This framework provides dozens of signature and encryption algorithms, but you do not need all of them. Most applications only support 1 or 2 algorithms.

You should only use necessary algorithms. For example, HS384 algorithm may be avoided if you already have HS256 and HS512.

### Avoid weak algorithms

Some algorithms are not recommended as there are known security issues:

* `none`: this algorithm is not a real algorithm. It should only be used when other security means exist. An encrypted connection is certainly not enough!
* `RSA1_5`: there are known attacks using this algorithm. If you can avoid its use, then do it.

## Keys and key sets

### Key size

A small key size is as secure as a password like `123456789`.

* RSA keys: 2048 bits at least. Since 4.2.6, a key beyond the limits of OpenSSL is refused.
* HMAC keys (`HS256`, `HS384`, `HS512`): at least as long as the output of the hash function, that is 256, 384 and 512 bits ([RFC 7518 section 3.2](https://datatracker.ietf.org/doc/html/rfc7518#section-3.2)). The library does not check it: make sure of it when you create the key.
* Encryption keys (`dir`, `A*KW`, `A*GCMKW`): exactly the size the algorithm needs. The library checks it; see the [key requirements](../the-components/encrypted-tokens-jwe/encryption-algorithms.md#key-requirements).

In any case, you MUST use a true random number generator. Never build a key from a text secret, or from an environment variable that may be empty: the `PBES2-*` algorithms are the ones made for passwords.

### Additional information

It is highly recommended to set the following parameters to your key:

* `kid`: A unique key ID,
* `use`: indicates the usage of the key. Either `sig` (signature/verification) or `enc` (encryption/decryption).&#x20;
* `alg`: the algorithm allowed to be used with this key. A key with an `alg` parameter is never used with another algorithm, which matters in a key set shared by several algorithms.

### Key rotation

A key is fine but may be cracked e.g. by bruteforce. Changing your keys after several days or weeks is encouraged.

### Key sets fetched from a URL

Fetch a key set only from a URL your application trusts, such as one written in its configuration. The `jku` and `x5u` header parameters of a token are chosen by its sender: never fetch them unless they are in an exact list of trusted URLs. Refuse the redirects too, by giving the factories an HTTP client whose `max_redirects` option is 0. See [Distant key sets](../the-components/key-jwk-and-key-set-jwkset/key-set-management.md#redirects).

### Key material in logs

Since 4.2.6, the library marks the parameters that carry key material with `#[\SensitiveParameter]`, so that they are not written in stack traces. A custom algorithm should do the same: see [Custom algorithm](../advanced-topics/custom-algorithm.md#keeping-key-material-out-of-stack-traces). In production, also set `zend.exception_ignore_args = On`, as the `php.ini-production` file of PHP does.

## Token creation

### Header parameters

Broadly speaking, you should set your header parameter in the protected header. The use of the unprotected header should be limited to specific use cases.

With encrypted tokens, a header parameter must appear in **exactly one** of the three header locations — shared protected, shared unprotected and per-recipient — as required by [RFC 7516 section 7.2.1](https://datatracker.ietf.org/doc/html/rfc7516#section-7.2.1). The framework enforces it in both directions since 4.2, when the token is written and when it is read. Always put `alg` and `enc` in the shared protected header: it is the only one covered by the AAD, and they are not read from the shared unprotected header.

When using encrypted tokens, the claims `iss` and `aud` should be duplicated into the header. This will avoid unwanted decryption when tokens are sent to a wrong audience.

### Payload and claims

There is no size constraint for the payload, but when tokens are used in a web context, it should be as small as possible. When used, claims should be limited to the minimum.

Does your application really need to get all the information about a user? For each context, you should choose carefully the claims you want to use.

#### Token unique ID

A unique token ID should be set to all tokens you create. The associated claim is `jti`.

This claim is highly recommended as it can prevent replay attacks.

#### Time indicators

The JWT specification introduces several claims to limit the period of validity of the tokens:

* `exp`: expiration time,
* `iat`: issuance time,
* `nbf`: validity point in time.

These claims are not mandatory, but it is recommended to define a period of time for the token validity. When used, the expiration time should be appropriate to its context in your application. A security token with 2 weeks lifetime is something you should avoid.

#### Issuer and audience

The claims `iss` (issuer) and `aud` (audience) should always be set. When duplicated in the header, their values MUST be identical.

## Application communication

### Secured connection

Unless you use encrypted tokens, you should use a secured connection when transmitting tokens between parties. A secured communication is not only needed when transmitting tokens, but also when you exchange keys and key sets with other applications.

## Loading process

When you receive a token, the following steps should be followed in this order. If one failed, you **must** reject the whole token.

1. Unserialize the token
2. For each signature/recipient (may be possible when using the Json General Serialization Mode):
   1. Check the complete header (protected and unprotected)
   2. Verify the signature (JWS) or decrypt the token (JWE)
   3. Check the claims in the payload (if any)

!!! warning

    Regarding header verification, it is important to verify **ALL** of them. There are known vulnerabilities on e.g. algorithm swapping (`alg` changed to `none`) or Denial Of Service (`p2c` set to a very high value for overloading the server).

### Unserialize the token

You should only use the serialization mode(s) you need. If you intend to use your tokens in a web context, then use only the Compact Serialization. If an error occurred during this process, you should consider the token as invalid.

### Bound what a token may cost

A token is read before anything about it is verified, so whoever sends it chooses its size and its shape:

* Limit the size of the request bodies and headers at the web server. Some servers accept request headers of about 1 MB by default.
* Since 4.2.6, the serializers decode at most 4,096 JSON values per token: see [Bounded JSON decoding](../advanced-topics/serialization.md#bounded-json-decoding). This budget does not replace a size limit: the claims and the key sets are not bounded.
* If you accept the JSON General serialization, set the maximum number of [signatures](../the-components/signed-tokens-jws/jws-loading.md#maximum-number-of-signatures) or [recipients](../the-components/encrypted-tokens-jwe/jwe-loading.md#maximum-number-of-recipients) of your loaders, or do not register `jws_json_general` and `jwe_json_general`. Without a maximum, their number is not limited.
* Accept the `PBES2-*` algorithms only from senders you trust: each recipient asks for its own iteration count, up to the `max_count` of the algorithm.

### Check the header

It is strongly recommended that all header parameters are checked before the cryptographic operations (signature verification or content decryption).

Please note that unknown header parameters must be ignored. If your token is verified, those parameters should not be used.

When used, unprotected header parameters should be handled with care. They are not covered by the signature or the AAD: never let them drive a cryptographic decision, and never trust a value you only found there.

### Signature verification / payload decryption

Let the component do its job. The most important step for developers is to ensure that the right key/key set is used.

### Check the claims

This step is only required if the payload contains claims. When present, you should always check the `exp`, `iat`, `nbf`, `iss` and `aud` claims. Application-specific claims should also always be checked.

The whole token should be rejected in case of failure. Unknown claims should be ignored.

## Stay tuned

You should subscribe to security forums and maintain a continuous technological watch. The tokens may be compromised because of malicious attacks on the algorithms, keys or other components related to the JWT (directly or indirectly).

The [Security group on Stack Exchange](https://security.stackexchange.com/) is a good start.
