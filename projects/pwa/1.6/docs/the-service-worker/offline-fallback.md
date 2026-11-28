# Offline fallbacks

Without a network, a navigation shows the error page of the browser, and an image or a font is simply missing. The service worker can answer these failed requests instead: with an offline page for a navigation, a placeholder image, or a font. The offline fallbacks work with or without [Workbox](workbox/README.md).

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        offline_fallback:
            page: 'app_offline_page'
            image: 'images/offline.svg'
            font: 'fonts/normal.ttf'
```

`page` can be a relative URL, a route name or a route name with parameters. See [URL parameter](../the-manifest/shortcuts.md#url-parameter) for more information.

`image` and `font` refer to assets delivered by Asset Mapper or an URL to the font file.

The fallbacks are cached when the service worker installs, in the `offline` cache unless `cache_name` says otherwise. A navigation that fails is then answered with the page, a failed image request with the image, and a failed font request with the font.

!!! warning

    **Moved in 1.6.0.** The options used to be under `pwa.serviceworker.workbox.offline_fallback`. That place still works until 2.0.0, with the same options, and triggers this deprecation:

    ```
    Since spomky-labs/pwa-bundle 1.6.0: The "pwa.serviceworker.workbox.offline_fallback" option is deprecated
    and will be removed in 2.0.0. Move it to "pwa.serviceworker.offline_fallback": it takes the same options,
    and the offline fallbacks work there with or without Workbox.
    ```

    Writing both fails. See the [upgrade guide](../upgrades/from-1.5.x-to-1.6.0.md#deprecated-workboxoffline_fallback).

## One offline page per URL

`page` resolves to a single URL. With localized routes, every visitor gets the offline page of the same locale, whatever the language of the page they were trying to reach.

Since 1.6.0, `pages` lists offline pages chosen by the URL of the failed navigation:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
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

    The patterns are written into the service worker as strings, and compiled when a navigation is tested against them. They are tried in order, so a navigation reaches an invalid pattern when no pattern before it matches. An invalid pattern does not prevent the service worker from installing, but:

    * with Workbox, the patterns are only tested when a navigation fails, and no offline page can be served to a navigation that reaches the invalid one;
    * without Workbox, the page is chosen before the network is tried, so the patterns are tested on **every** navigation. The invalid one throws on each navigation that reaches it, and the bundle leaves that navigation alone: online, it loads as usual, offline, no offline page is served.

    Test your patterns.

## Refreshing the fallbacks

The fallbacks are cached once, when the service worker installs, and a browser installs a service worker again only when its script changes. When a fallback changes but its URL does not, for instance when the offline page is reworded, the script stays the same and visitors keep the old copy.

Since 1.6.0, `version` is written into the service worker. Change it whenever a fallback changes:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        offline_fallback:
            page: 'app_offline'
            version: '2025-01-15'
```

The new script makes the browser install the service worker again, and the fallbacks are cached again, fetched past the HTTP cache, into the same cache: no cache is left behind. The value is any string, an integer being read as one.

The offline cache is not emptied first, with or without Workbox: a fallback you stop listing keeps its copy in it.

## With Workbox

The fallbacks are cached by an install task of the bundle, and served by the catch handler of the Workbox router: a request whose strategy fails, or that no route matches and that the network cannot answer, gets its fallback. See [Custom service worker rule](custom-service-worker-rule.md#registerinstalltaskcallback-priority-100) for the order of the install tasks.

## Without Workbox

The same options work with Workbox disabled:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        offline_fallback:
            page: '/offline'
            image: '/images/offline.svg'
        workbox:
            enabled: false
```

The bundle then writes two plain listeners, and calls neither Workbox nor any function of its own:

```javascript title="the listeners written into /sw.js" linenums="1"
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open("offline").then(cache =>
    cache.addAll(["/offline","/images/offline.svg"].map(url => new Request(url, { cache: 'reload' })))
  ));
});
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const fallbacks = {"pageFallback":"/offline","imageFallback":"/images/offline.svg"};
  let fallback;
  if (request.mode === 'navigate') {
    fallback = fallbacks.pageFallback;
  } else if (request.destination === 'image') {
    fallback = fallbacks.imageFallback;
  }
  if (!fallback) {
    return;
  }
  event.respondWith(fetch(request).catch(async () => (await caches.match(fallback, { cacheName: "offline" })) ?? Response.error()));
});
```

* The `install` listener caches the same URLs as with Workbox: the page, the pages, the image and the font, each once, fetched past the HTTP cache with `cache: 'reload'`. With a `version`, it is written at the start of this listener.
* The `fetch` listener only answers the requests it has a fallback for: the navigations when `page` or `pages` is set, the image requests when `image` is set, the font requests when `font` is set. It fetches them from the network, and serves the fallback when the network fails, or a network error when the fallback is missing from the cache. With `pages`, the page is chosen as described [above](#one-offline-page-per-url).
* Every other request is left untouched, to the listeners that follow, those of your own source included.

These listeners come first in the compiled service worker: your own source, the `src` option, is appended after every rule of the bundle.

!!! warning

    `event.respondWith()` stops the event. For the requests the bundle answers, the `fetch` listeners of your own source are **not called**: every navigation with a `page`, every navigation one of the patterns matches with `pages` alone, and every image or font request with an `image` or a `font`. A listener of yours that handles these requests has to give way, or the fallback has to go.

!!! info

    The `fetch` listener fetches the request itself and never reads `event.preloadResponse`. The bundle does not enable [navigation preload](workbox/navigation-preload.md) without Workbox, but if your own source does, every navigation answered here is fetched twice.

[Cache cleaning](workbox/cache-cleaning.md) is a Workbox feature: without Workbox, the bundle never deletes a cache, the offline one included.

## Options

| Option | Default | Description |
| --- | --- | --- |
| `cache_name` | `offline` | The cache the fallbacks are stored in |
| `version` | `null` | Written into the service worker: changing it caches the fallbacks again |
| `page` | `null` | The page served to a failed navigation: a URL, a route name with its parameters, or an asset |
| `pages` | `[]` | Pages chosen by the URL of the failed navigation, each with a `page` and a `match` pattern |
| `image` | `null` | The image served when an image request fails |
| `font` | `null` | The font served when a font request fails |
