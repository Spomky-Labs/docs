# Offline fallbacks

Workbox makes it easy to create robust offline experiences in web applications. When a user navigates to a page without an internet connection, instead of showing an error, your application can serve a predefined fallback page, image or font.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            offline_fallback:
                page: 'app_offline_page'
                image: 'images/offline.svg'
                font: 'fonts/normal.ttf'
```

`page` can be a relative URL, a route name or a route name with parameters. See [URL parameter](../../the-manifest/shortcuts.md#url-parameter) for more information.

`image` and `font` refer to assets delivered by Asset Mapper or an URL to the font file.

The fallbacks are cached when the service worker installs, in the `offline` cache unless `cache_name` says otherwise. A navigation that fails is then answered with the page, a failed image request with the image, and a failed font request with the font.

## One offline page per URL

`page` resolves to a single URL. With localized routes, every visitor gets the offline page of the same locale, whatever the language of the page they were trying to reach.

Since 1.6.0, `pages` lists offline pages chosen by the URL of the failed navigation:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            offline_fallback:
                page:
                    path: 'app_offline'
                    params:
                        _locale: 'en'
                pages:
                    - page:
                          path: 'app_offline'
                          params:
                              _locale: 'fr'
                      match: '^https?://[^/]+/fr(/|$)'
                    - page:
                          path: 'app_offline'
                          params:
                              _locale: 'de'
                      match: '^https?://[^/]+/de(/|$)'
```

Each entry needs both keys:

* `page` is given like `page` above: a URL, a route name with its parameters, or an asset. A route is resolved with its own parameters, so each entry can set its `_locale`.
* `match` is a JavaScript regular expression, written without delimiters or flags. It is given to `new RegExp()` and tested against the **full URL** of the failed navigation, e.g. `https://example.com/fr/products?page=2`: anchor it after the host to match a path prefix, as the example does.

A failed navigation gets the first page whose pattern matches its URL, in the order of the list, and `page` when none matches. `page` stays optional: without it, a navigation that matches no pattern gets the usual network error.

Every page is cached when the service worker installs, each URL once, even when `page` and an entry point at the same one.

!!! warning

    The patterns are written into the service worker as strings and only compiled when a navigation fails. An invalid pattern does not prevent the service worker from installing, but no offline page can be served to a navigation that reaches it. Test your patterns.

## Refreshing the fallbacks

The fallbacks are cached once, when the service worker installs, and a browser installs a service worker again only when its script changes. When a fallback changes but its URL does not, for instance when the offline page is reworded, the script stays the same and visitors keep the old copy.

Since 1.6.0, `version` is written into the service worker. Change it whenever a fallback changes:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            offline_fallback:
                page: 'app_offline'
                version: '2025-01-15'
```

The new script makes the browser install the service worker again, and the fallbacks are cached again, fetched past the HTTP cache, into the same cache: no cache is left behind. The value is any string, an integer being read as one.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `cache_name` | `offline` | The cache the fallbacks are stored in |
| `version` | `null` | Written into the service worker: changing it caches the fallbacks again |
| `page` | `null` | The page served to a failed navigation: a URL, a route name with its parameters, or an asset |
| `pages` | `[]` | Pages chosen by the URL of the failed navigation, each with a `page` and a `match` pattern |
| `image` | `null` | The image served when an image request fails |
| `font` | `null` | The font served when a font request fails |
