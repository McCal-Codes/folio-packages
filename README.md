# Folio packages

Themes, tweaks and layouts for [Folio](https://github.com/McCal-Codes/folio), published as a **source** the app can
add. Anyone can open a pull request here; the site this repo builds is a signed package list that Folio reads.

Folio is a launcher for foldables that looks and behaves like iOS. A package doesn't run code: it configures things
Folio can already do, and its page in the Market says exactly which ones.

## Add it in Folio

Market → Sources → **Add a source**, and paste:

```
https://mccal-codes.github.io/folio-packages/
```

Folio shows the source's key fingerprint before it trusts it, and pins that key from then on. The Market is in Folio
0.7.0; on an earlier release, every theme and tweak it hands out is already in Settings.

## What's in here

```
packages/<package-id>/
  manifest.json      what it is, and which Folio capabilities it configures
  depiction.json     its page in the Market
  tweaks.json        for a tweak package: which built-in tweak it turns on
  assets/            icon and screenshots (png, webp or jpg)
template/hello-tweak/  a package to copy
tools/build.py         packs every package, builds the index and signs it
```

Everything under `site/` is built, never committed. The format is documented in
[Folio Package Format v1](https://github.com/McCal-Codes/folio/blob/main/docs/sdk/format-v1.md), and the JSON Schemas
in that repo give editors autocomplete.

## Publish a package

1. Copy `template/hello-tweak` to `packages/<your-id>/` and edit it. Ids are reverse-DNS and lowercase:
   `dev.maya.sunset-icons`.
2. Put a square icon of at least 180 px at `assets/icon.png`, and a screenshot or two beside it.
3. Run `python3 tools/build.py` and open `site/index.json` to see what Folio will read.
4. Open a pull request. CI checks the same things the app does; see [CONTRIBUTING.md](CONTRIBUTING.md).

## Pictures

A picture is a relative path on **this site**, not something read out of the package file, because the Market shows a
package's page before anything is downloaded. `tools/build.py` copies each package's `assets/` to
`assets/<package-id>/` on the site and rewrites the paths, so you keep them in one folder and don't think about it.

## Trust

The index is signed with a key that lives only in this repo's secrets; the public half is published as `key.pub` and
shown to the user as a fingerprint. Every package in the index carries its SHA-256 and size, and Folio checks both
before it opens a file. A package that turns out to be harmful goes in `revoked.json`, which is signed the same way
and turns it off on phones that already have it.

## Licence

The repo is MIT. Each package keeps its own licence, named in its manifest.
