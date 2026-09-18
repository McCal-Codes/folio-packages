# Contributing a package

A pull request adds one folder under `packages/`. CI runs the same checks the app does, and a person reads it before
it goes in.

## What CI checks

- The manifest and depiction parse, and match the v1 schemas.
- The id is reverse-DNS, lowercase and not already taken; the version follows dpkg ordering, and is higher than the
  one already published.
- Only the capabilities Folio has, and only the permissions the manifest declares.
- Pictures are png, webp or jpg, under 2 MB each; the icon is square and at least 180 px.
- The packed `.foliopkg` is under 20 MB and contains no executable file.
- Text is in English (`en`) at minimum; other languages are welcome beside it.

## What a reviewer looks for

- The description says what the package changes, in plain words, without marketing.
- The screenshots are of the package, on a phone, not mockups or stock art.
- Nothing claims to be by someone it isn't. A package that copies another's name or artwork is refused.
- Credit where a tweak is inspired by an iOS jailbreak tweak, the way Folio credits its own.

## Updating a package

Raise the version and add a `changelog` entry saying what changed. The Market shows that entry as "What's new", so
write it for the person deciding whether to update.

## Taking a package down

Open an issue, or mail the address in the Folio repo. A package that is harmful, stolen or broken beyond repair is
added to `revoked.json` with a reason: Folio then refuses to install it, says why on its page, and lets anyone who
already has it remove it. Nothing is deleted quietly - a pulled package keeps its place with the reason showing.
