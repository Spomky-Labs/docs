# From v9 to v10

Normally nothing to do. The release updated the dependencies and raised the minimum PHP version to 7.2.

What changed:

* New public methods on the interfaces.
* A dedicated interface for the factory, `FactoryInterface`.
* **Both arguments of `getQrCodeUri()` became required.** The Google Charts API it used to default to was
  deprecated in April 2019, so there is no sensible default left to fall back on. Pass the URI of the
  service and the placeholder to replace in it — or, better, render the QR code yourself. See
  [QR codes](../configuring-an-application/qr-codes.md).
* The `mbstring` extension became a required dependency. It no longer is: v11 calls nothing from it.
