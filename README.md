# Candango OpenLDAP COPR

This repository contains the packaging recipe and validation material for the
[`candango/openldap`](https://copr.fedorainfracloud.org/coprs/candango/openldap/)
COPR project.

The goal is to provide an OpenLDAP package for Rocky Linux 10 with validated
native Argon2id support. Bcrypt compatibility is provided through the system
`libxcrypt` implementation and OpenLDAP's `{CRYPT}` scheme.

## Current status

The repository is currently a packaging scaffold and is **not ready for
production deployment or release**. Source pinning, the complete RPM spec,
artifact builds and end-to-end validation are still required.

## Requirements

Local development requires:

- RPM build tooling, including `rpmspec` and `rpmbuild`;
- GNU Make;
- the dependencies declared by `openldap.spec`;
- an approved Rocky Linux 10 build and validation environment for release work.

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
tokens or other secret material. COPR builds must use explicit, pinned source
inputs and must not depend on arbitrary network access during the build.

Release artifacts require package provenance, dependency review, controlled
signing outside the public repository and approved Rocky Linux validation.

## Licensing

Original repository scaffolding is MIT-licensed. The OpenLDAP source and RPM
retain the upstream OpenLDAP Public License and all applicable upstream notices.
The repository's MIT license must not be used as the OpenLDAP package license.
