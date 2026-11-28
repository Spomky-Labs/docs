# Installation

To install the bundle, the recommended way is using Composer:

```sh
composer require spomky-labs/pwa-bundle
```

No Flex recipe exists for this bundle. The configuration file is yours to create, and it grows as you integrate the features. The [`pwa:create:config` command](#creating-the-configuration-file) writes a first one for you; an empty one is enough to start with:

```yaml title="/config/packages/pwa.yaml" linenums="1"
pwa: ~
```

The integration in your application is very simple. You are only required to add a Twig function inside the end of the `<head>` tag of your HTML pages.

```twig linenums="1"
<!DOCTYPE html>
<html lang="en">
<head>
  {{ pwa() }}
</head>
<body>
  ...
</body>
</html>
```

!!! info

    You may need to clear the cache after the bundle is installed

## Creating the configuration file

Since 1.6.0, `pwa:create:config` writes `config/packages/pwa.yaml` for you: the manifest, the icons and the favicons generated from one source image, and the service worker. Run it without any option to be guided step by step:

```sh
php bin/console pwa:create:config
```

```
 Name of the application [Hacker News]:
 > HackerNews PWA
 Short name, displayed under the icon [HackerNews]:
 >
 Description of the application (optional):
 > A HackerNews implementation based on Symfony
 URL loaded when the application starts [/]:
 >
 Display mode [standalone]:
  [0] fullscreen
  [1] standalone
  [2] minimal-ui
  [3] browser
 >
 Theme color [#ffffff]:
 >
 Background color [#ffffff]:
 >
 Source image of the application (leave empty to skip):
 > images/logo.svg
 Generate the favicons from this image? (yes/no) [yes]:
 >
 Enable the service worker (offline support, caching, push notifications)? (yes/no) [yes]:
 >
 Path to the service worker source file [sw.js]:
 >

 [OK] The configuration file "config/packages/pwa.yaml" has been created.
```

Every value has an option of its own, so the command can be scripted. The command only asks for what the options leave out, and with `--no-interaction` it asks nothing and takes the defaults for the rest:

```sh
php bin/console pwa:create:config --no-interaction \
    --name="HackerNews PWA" \
    --description="A HackerNews implementation based on Symfony" \
    --icon=images/logo.svg
```

With the Imagick extension loaded, both produce this file:

```yaml title="/config/packages/pwa.yaml" linenums="1"
# See https://docs.spomky-labs.com/pwa/ for the complete list of options.
pwa:
    image_processor: imagick
    manifest:
        enabled: true
        name: 'HackerNews PWA'
        short_name: HackerNews
        description: 'A HackerNews implementation based on Symfony'
        start_url: /
        display: standalone
        theme_color: '#ffffff'
        background_color: '#ffffff'
        icons:
            -
                src: images/logo.svg
                sizes: [48, 72, 96, 128, 144, 168, 192, 256, 512]
                format: png
    favicons:
        enabled: true
        default:
            src: images/logo.svg
            background_color: '#ffffff'
    startup_images:
        enabled: true
    serviceworker:
        enabled: true
        src: sw.js
```

| Option | Description |
|--------|-------------|
| `--name` | The name of the application. Defaults to the name of the project directory |
| `--short-name` | The short name, displayed under the icon. Defaults to the name, cut to 12 characters on a word boundary |
| `--description` | The description of the application, left out when empty |
| `--start-url` | The URL loaded when the application starts, `/` by default |
| `--display` | The display mode: `fullscreen`, `standalone` (default), `minimal-ui` or `browser` |
| `--theme-color` | The theme color, `#ffffff` by default |
| `--background-color` | The background color, `#ffffff` by default |
| `--icon` | The source image of the icons and the favicons: an Asset Mapper logical path or a path to a file |
| `--favicons` / `--no-favicons` | Whether the favicons are generated. Defaults to yes when `--icon` is given |
| `--serviceworker` / `--no-serviceworker` | Whether the service worker is enabled, yes by default |
| `--serviceworker-src` | The service worker source file, `sw.js` by default |
| `--image-processor` | `imagick`, `gd` or `none`. Detected when omitted |
| `--path` | The file to write, `config/packages/pwa.yaml` by default |
| `-f`, `--force` | Overwrite the file if it already exists |
| `--dry-run` | Print the configuration on the standard output instead of writing it |

A few things the command does on its own:

* **The image processor**, when `--image-processor` is omitted, is detected and only written when an icon is given. Imagick is preferred, being the only one able to read an SVG source, then GD. Asking for `imagick` or `gd` without its PHP extension fails, rather than writing a configuration that breaks the container.
* **The favicons** need a source image: `--favicons` without `--icon` fails. When the favicons are enabled, `startup_images.enabled: true` is written next to them, so the iOS [startup images](favicons/startup-images.md) are kept without the deprecation of their implicit default.
* **The service worker source file** is created empty in `assets/` when it does not exist, as Asset Mapper needs a file to serve. The bundle populates it.
* **An existing file** is never overwritten without `--force`, or a confirmation in interactive mode.

`--dry-run` writes the configuration and nothing else on the standard output, so it can be redirected:

```sh
php bin/console pwa:create:config --no-interaction --dry-run > config/packages/pwa.yaml
```

## Twig function options

The `pwa()` Twig function accepts several optional parameters to control what is injected:

```twig
{{ pwa(
    injectThemeColor: true,
    injectFavicons: true,
    injectSW: true,
    swAttributes: {},
    locale: null,
    injectResourceHints: true,
    injectSpeculationRules: true
) }}
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `injectThemeColor` | bool | `true` | Inject theme color meta tags |
| `injectFavicons` | bool | `true` | Inject favicon link tags, and the [startup image](favicons/startup-images.md) ones |
| `injectSW` | bool | `true` | Inject service worker registration script |
| `swAttributes` | object | `{}` | Custom attributes for the service worker script tag |
| `locale` | string | `null` | Locale for manifest (auto-detected from request if null) |
| `injectResourceHints` | bool | `true` | Inject [resource hints](performance/resource-hints.md) (preconnect, dns-prefetch, preload) |
| `injectSpeculationRules` | bool | `true` | Inject [speculation rules](performance/speculation-rules.md) for prefetch/prerender |

### Example: Disable resource hints

```twig
{{ pwa(injectResourceHints: false) }}
```

### Example: Localized manifest

```twig
{{ pwa(locale: app.request.locale) }}
```
