#!/bin/bash
##
## Copyright 2026 Flavio Garcia
##
## signall.sh    Sign all packages present on $ROOT.
##
## Author: Flavio Garcia <piraz@candango.org>
export GNUPGHOME=<GNUPGHOME>
export SIGNING_KEY="<SIGNING_KEY>"
ROOT=<THE-ROOT>

gpg --list-keys --with-fingerprint "$SIGNING_KEY"

packages=(
  "$ROOT"/RPMS/x86_64/*.rpm
  "$ROOT"/SRPMS/*.src.rpm
)

packages=(
  "$ROOT"/rpm/rocky/10/x86_64_v2/*.rpm
)
for pkg in "${packages[@]}"; do
  rpmsign --addsign \
    --define "%_gpg_name ${SIGNING_KEY}" \
    "$pkg"
done

for pkg in "${packages[@]}"; do
     rpm --checksig -v "$pkg"
done
