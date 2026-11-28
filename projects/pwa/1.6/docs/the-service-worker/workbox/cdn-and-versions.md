# Workbox files

The bundle ships the Workbox libraries and serves them from your own server: no third-party request, and a Content Security Policy that needs no exception.

**The bundled version is `7.4.1`.** It is copied to your public folder by `php bin/console pwa:compile`, and there is nothing to configure.

## Choosing the version is deprecated

!!! warning

    `use_cdn` and `version` are deprecated since 1.6.0 and will be removed in 2.0.0.

Everything the bundle generates — the imports, the caching strategies, the plugins, the helpers — is written against the API of the Workbox version it ships. Pinning another version, or fetching one from a CDN, produced a service worker written for one version and running against another. It failed in the browser rather than at compile time, which is the worst place to find out.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            config:
                use_cdn: true       # deprecated since 1.6.0
                version: '7.3.0'    # deprecated since 1.6.0
```

A pinned version still compiles until 2.0.0:

* With `use_cdn: false`, the default, the files are served from your own server, and only the bundled ones can be. A pinned version, `config.version` or the flat `version`, is ignored, the 7.4.1 files are served, and the bundle logs this warning when it compiles them, here for `version: '7.3.0'`:

    ```
    The Workbox version "7.3.0" is ignored: only the bundled version "7.4.1" can be served from the
    application. Remove the "version" option from the Workbox configuration.
    ```

    It reaches your logs through the [default logger](../../development.md#default-logger): the `pwa` channel with MonologBundle, or, without it, the logger of FrameworkBundle, which prints warnings only for a command run with `-v`. With [`pwa.logger`](../../development.md#custom-logger) set, it goes to that service.

* With `use_cdn: true`, the service worker imports the pinned version from the CDN.

**What to do:** remove both options. The bundled files are what the generated service worker expects.

!!! info

    Both spellings are deprecated: the flat `workbox.use_cdn` and `workbox.version`, deprecated since 1.5.0, and their `workbox.config.*` counterparts. An application still using the flat ones is told twice — once for the option it wrote, once for the section the value is migrated into. Removing the option silences both.

### Compiling again

The files have always been written under `workbox_public_url`, whatever the version, with the same names. Once the options are removed, compile again: `pwa:compile` writes the 7.4.1 files over those of the former version, and nothing is left behind.

```bash title="terminal"
php bin/console pwa:compile
```

## Where the files are served from

The libraries are written under `workbox_public_url`, which is **not** deprecated — where your own server exposes them is yours to decide.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            config:
                workbox_public_url: '/assets/workbox'
```

!!! info

    `workbox_public_url` moved under `workbox.config` in 1.5.0. Its old location still works but is deprecated, and will be removed in 2.0.0.

## Debug logging

Workbox logs what every route and strategy does in the browser console, and loads its development builds to do so. The `debug` option is `true` by default; setting it to `false` emits `workbox.setConfig({debug: false})` in the service worker, which silences the logs and switches to the production builds.

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa:
    serviceworker:
        enabled: true
        src: "sw.js"
        workbox:
            config:
                debug: false
```
