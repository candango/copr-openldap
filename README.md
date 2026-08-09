# Candango OpenLDAP RPM Repository

This repository contains the packaging recipe and validation material for the
Candango OpenLDAP RPM repository at `https://rpm.candango.org/`.

The goal is to provide an OpenLDAP package for Rocky Linux 10 with validated
native Argon2id support. Bcrypt compatibility is provided through the system
`libxcrypt` implementation and OpenLDAP's `{CRYPT}` scheme.

## Current status

The repository is still under controlled packaging and validation work. Do
not deploy an artifact until source pinning, package inspection, signing and
approved Rocky Linux validation have passed.

## Requirements

Local development requires:

- RPM build tooling, including `rpmspec` and `rpmbuild`;
- GNU Make;
- the dependencies declared by `openldap.spec`;
- an approved Rocky Linux 10 build and validation environment for release work.

## Install from the public repository

The target is Rocky Linux 10 x86_64. Keep EPEL enabled for `libargon2` and
other approved dependencies, but exclude EPEL's competing OpenLDAP packages.
The Candango repository supplies the OpenLDAP packages.

Install the repository configuration and public verification key over HTTPS:

```bash
sudo dnf install -y curl dnf-plugins-core epel-release
sudo dnf config-manager --set-enabled crb

sudo curl --fail --location --proto '=https' --tlsv1.2 \
  --output /etc/yum.repos.d/candango-rpm.repo \
  https://rpm.candango.org/candango-rpm.repo

sudo curl --fail --location --proto '=https' --tlsv1.2 \
  --output /etc/pki/rpm-gpg/RPM-GPG-KEY-candango \
  https://rpm.candango.org/keys/RPM-GPG-KEY-candango
```

Verify the downloaded public key before importing it. The expected fingerprint
is:

```text
CBEC 5A0C FAB7 C97A ECF8 A691 457D 3592 7250 0A9B
```

```bash
gpg --show-keys --with-fingerprint \
  /etc/pki/rpm-gpg/RPM-GPG-KEY-candango
sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-candango
```

Exclude OpenLDAP packages from EPEL without disabling EPEL itself:

```bash
sudo dnf config-manager \
  --setopt=epel.excludepkgs='openldap*' \
  --save
sudo dnf clean all
sudo dnf makecache
```

Install the Candango packages:

```bash
sudo dnf install -y openldap openldap-clients openldap-servers
```

Confirm that installed OpenLDAP packages carry the Candango release and that
`libargon2` remains resolved from the approved EPEL dependency path. This
procedure is for validated release artifacts; use the lab runbook before any
production promotion.

## Common commands

Validate the spec and local package checks:

```bash
make spec-check
make test
```

Build the source and binary RPMs after all source and packaging TODOs have been
resolved:

```bash
make build
```

Remove local RPM build directories:

```bash
make clean
```

Do not publish or deploy artifacts produced before the complete validation
workflow passes.

## Repository layout

```text
openldap.spec                 RPM package definition
sources                       Pinned source archives and checksums
patches/                      Local upstream patches, when required
tests/                        Non-destructive package and integration checks
docs/                         Build, configuration and validation guidance
Makefile                      Local build and validation targets
```

## Password schemes

- `{ARGON2}` is the preferred native OpenLDAP server-side scheme for this
  project and requires the Argon2 password module.
- `{CRYPT}$2b$...` provides bcrypt compatibility through Rocky `libxcrypt`.
- `{SSHA}`, `{SHA}`, `{SMD5}` and `{MD5}` are compatibility schemes only.
- `{ARGON2ID}` and `{BCRYPT}` are not separate scheme names in this packaging
  path.

Argon2id support must be demonstrated using the built RPM. It must not be
inferred only from a configure flag or package description.

## Security and release policy

Do not commit credentials, private keys, LDAP dumps, generated password hashes,
tokens or other secret material. Builds must use explicit, pinned source
inputs and must not depend on arbitrary network access during the build.

Release artifacts require package provenance, dependency review, controlled
signing outside the public repository and approved Rocky Linux validation.

## Licensing

Original repository scaffolding is MIT-licensed. The OpenLDAP source and RPM
retain the upstream OpenLDAP Public License and all applicable upstream notices.
The repository's MIT license must not be used as the OpenLDAP package license.
