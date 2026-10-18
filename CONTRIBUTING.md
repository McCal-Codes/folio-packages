# Contributing

There are two ways to get a package to people, and neither one needs permission from anyone.

## 1. Run your own repository

A source is static files on any HTTPS host: an index, a signed pointer to it, and a package file per package. That's
all Folio reads, so GitHub Pages, a personal site or anything that serves files will do.

1. Copy this repo — `tools/build.py`, the Action and `template/hello-tweak` are the whole machine.
2. Make your key with `bash tools/keygen.sh` and put the private half in your repo's secrets as `FOLIO_SIGNING_KEY`.
3. Push. The Action builds and signs your site, and your source's address is what people add in Folio.

Your repo, your key, your rules about what you list — the same way Sileo repos work. Folio shows anyone adding your
source its key fingerprint first, and pins it, so you never have to ask them to trust anything twice.

Tell people how to add it:

```
Market → Sources → Add a source → https://<you>.github.io/<your-repo>/
```

## 2. Send it here

This repo is the shared one, for people who'd rather not run a source. Open a pull request that adds one folder under
`packages/`. Tweaks are welcome — a tweak package configures things Folio can already do, and its page says which
ones — as are themes, layouts and wallpapers.

CI runs the same checks the app does, and a person reads it before it goes in.

### What CI checks

Folio's own validator, pinned to a known Folio commit, checks each package on its own:

- The manifest, depiction and tweaks parse and match the v1 schemas.
- Only the capabilities Folio has, only the permissions the manifest declares, and no reserved kinds.
- Every picture the manifest and depiction name is there.

House rules (`tools/check-submission.py`) check what a schema can't:

- The folder is named after the package id, and the id isn't the template's or in Folio's own `com.mccal.` namespace.
- Only JSON and pictures (png, webp or jpg), each file under 2 MB and the package under 20 MB.
- Every link is `https://`.

On `main`, the signed site is checked again as a whole before it is published. Run the same checks yourself before
opening a pull request:

```sh
python3 tools/check-submission.py
python3 tools/build.py
```

Since each folder is named after its id, two packages can't share one. Not automatic yet, so a reviewer checks them:
that the version is higher than the one already published, and that the icon is square and at least 180 px.

### What a reviewer looks for

- The description says what the package changes, in plain words, without marketing.
- The screenshots are of the package, on a phone, not mockups or stock art.
- Nothing claims to be by someone it isn't. A package that copies another's name or artwork is refused.
- Credit where a tweak is inspired by an iOS jailbreak tweak, the way Folio credits its own.

## Listing a source someone else runs

A repo that's worth finding can be listed in [`sources.md`](sources.md) with a pull request: its address, who runs it,
and a line about what's on it. Folio doesn't read that file — it's for people. A listed source is still added by hand
and still shows its fingerprint, and being listed here isn't a review of what it contains.

## Signing your package

Optional, and worth doing if you plan to publish more than once.

A repo signature says "this list came from this repo, unchanged". It says nothing about who wrote a package — so
without an author signature, a mirror could carry your package and change it, and someone else could publish under
your package's name. An author signature fixes both.

```bash
openssl ecparam -name prime256v1 -genkey -noout -out dev.you.your-package.pem   # once, keep it offline
python3 tools/build.py --author-keys <folder holding that file>
```

Folio pins your key to your package id the first time it sees a signed copy, the way a phone pins an app's signing
key. After that, a copy signed by anyone else is refused, altered bytes are refused, and an unsigned copy of a
package that has always been signed is refused. Your package page says **signed by its developer**.

Two things follow: **keep the key**, because a new one means your package can't update itself on phones that already
have it, and **never commit it** — `.gitignore` covers `*.pem` and `authors/`, but that only helps if the key never
reaches the repo in the first place.

Unsigned packages are welcome too. Most first packages are, and Folio says so plainly rather than implying anything.

## Updating a package

Raise the version and add a `changelog` entry saying what changed. The Market shows that entry as "What's new", so
write it for the person deciding whether to update.

## Taking a package down

Open an issue, or mail the address in the Folio repo. A package that is harmful, stolen or broken beyond repair is
added to `revoked.json` with a reason: Folio then refuses to install it, says why on its page, and lets anyone who
already has it remove it. Nothing is deleted quietly — a pulled package keeps its place with the reason showing.

A source can be pulled the same way, by address. That only applies to sources listed here; one someone added by hand
is theirs, and Folio never disables it behind their back.
