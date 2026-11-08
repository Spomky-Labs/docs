# Additional authentication data (AAD)

The Additional Authenticated Data (AAD) is an input to an Authenticated Encryption operation. The AAD is integrity protected but not encrypted.

Its value can be any string you want that is needed by your application. With the example below, we will add a dummy AAD:

```php
$jwe = $jweBuilder
    ->withPayload('...')
    ->withSharedProtectedHeader([
        'enc' => 'A256CBC-HS512',
        'alg' => 'RSA-OAEP-256',
    ])
    ->addRecipient($recipient_key)
    ->withAAD('A,B,C,D')
    ->build();
```

**Note: when the AAD is set, the Compact Serialization mode is not available.**

## AES-CBC-HMAC tokens with an AAD

When a token has an AAD, the data authenticated by the content encryption is the encoded protected header, a period and the encoded AAD ([RFC 7516 section 5.1](https://datatracker.ietf.org/doc/html/rfc7516#section-5.1)). The authentication tag of `A128CBC-HS256`, `A192CBC-HS384` and `A256CBC-HS512` also covers the length of that data, AL ([RFC 7518 section 5.2.2.1](https://datatracker.ietf.org/doc/html/rfc7518#section-5.2.2.1)). Versions before 4.3 computed AL over the protected header only: other implementations refused these tokens, and the library refused theirs.

Since 4.3, AL covers the whole authenticated data:

* the tokens issued by 4.3 are accepted by other implementations, and theirs by 4.3;
* tokens issued by earlier versions still decrypt, with a deprecation notice. 5.0 refuses them: encrypt the stored ones again;
* earlier versions cannot decrypt the tokens issued by 4.3. Upgrade the applications that decrypt such tokens before the ones that issue them.

Tokens without an AAD, every compact token among them, and AES-GCM tokens are not affected.
