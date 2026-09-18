#!/usr/bin/env bash
# Makes the key this source signs with. Run it once, on a machine you trust, and never commit the result.
#
#   bash tools/keygen.sh
#
# It writes folio-source.pem (the private half) and prints the public half. Put the private half in this repo's
# secrets as FOLIO_SIGNING_KEY, keep an offline copy, and delete the file. If it's ever lost, a new key means every
# phone that trusts this source is asked about the change - which is exactly what a stolen key looks like, so don't
# lose it.
set -euo pipefail

openssl ecparam -name prime256v1 -genkey -noout -out folio-source.pem
chmod 600 folio-source.pem

echo
echo "Public key (base64 SPKI), published as key.pub:"
openssl ec -in folio-source.pem -pubout -outform DER 2>/dev/null | base64
echo
echo "Fingerprint Folio shows when someone adds this source:"
openssl ec -in folio-source.pem -pubout -outform DER 2>/dev/null | openssl dgst -sha256 -binary |
  xxd -p -c 32 | tr 'a-f' 'A-F' | fold -w4 | paste -sd' ' -
echo
echo "Now: gh secret set FOLIO_SIGNING_KEY < folio-source.pem   (then delete folio-source.pem)"
