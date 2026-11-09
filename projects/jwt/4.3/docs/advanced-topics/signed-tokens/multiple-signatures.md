# Multiple signatures

When you need to sign the same payload for several audiences, you may want to do it at once. The JWS Builder supports multiple signatures.

With the example below, we will create three signatures using three different algorithms (and signature keys):

```php
$jws = $jwsBuilder
    ->withPayload('...')
    ->addSignature($signature_key1, ['alg' => 'HS256'])
    ->addSignature($signature_key2, ['alg' => 'RS384'])
    ->addSignature($signature_key3, ['alg' => 'ES512'])
    ->build();
```

The variable `$jws` will be a valid JWS object with all computed signatures. Next step is the serialization of these signatures.

```php
use Jose\Component\Signature\Serializer;

$manager = new Serializer\JWSSerializerManager([
    new Serializer\CompactSerializer(),
    new Serializer\JSONFlattenedSerializer(),
    new Serializer\JSONGeneralSerializer(),
]);

$tokenWithAllSignatures = $manager->serialize('jws_json_general', $jws);
$compactTokenWithSignatureAtIndex1 = $manager->serialize('jws_compact', $jws, 1);
$flattenedTokenWithSignatureAtIndex2 = $manager->serialize('jws_json_flattened', $jws, 2);
```

## Loading a token with several signatures

A `JWSLoader` tries the signatures of a token one after the other, until one of them is verified, and the sender of the token decides how many there are. Since 4.2.6, the loader can reject a token that carries more signatures than you expect before trying any of them: see [Maximum number of signatures](../../the-components/signed-tokens-jws/jws-loading.md#maximum-number-of-signatures).

Since 4.3, loading a token with more than 10 signatures without setting a maximum is deprecated: 10 becomes the default maximum in 5.0.
