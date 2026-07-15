# Candango OpenLDAP COPR Context

## Mission

Build and distribute a Rocky Linux 10 OpenLDAP package with native Argon2id
password support for identity services.

The COPR project is:

```text
candango/openldap
```

This repository contains the packaging recipe, patches, build metadata,
validation notes and documentation for that COPR project. Local operator lab
access and transient host evidence belong in the ignored `LAB_INFO.md` file,
not in tracked project documentation.

## Repository

Local path:

```text
~/source/candango/copr-openldap
```

The repository is packaging/build infrastructure. It is not the LDAP data
directory and must never contain production LDAP dumps, passwords, private
keys, certificates, or generated secrets.

## Target platform

- Rocky Linux 10
- x86_64
- COPR chroot: `alma+epel-10-x86_64_v2`
- EPEL is included through the selected COPR chroot
- COPR build internet access should remain disabled
- No multilib, Fedora branching, module hotfixes, AppStream metadata, or Packit
  integration is required initially

The build must declare all source inputs explicitly and use checksums. Do not
make the build depend on arbitrary network downloads during `%build` or
`%install`.

## Source and packaging layout

The source repository should make the complete path visible:

```text
candango-openldap/
├── openldap.spec
├── sources
├── patches/
│   └── *.patch
├── tests/
├── docs/
├── Makefile
└── README.md
```

The packaging source must identify:

- the exact OpenLDAP upstream version;
- the upstream source URL and SHA256 checksum;
- every local patch and why it is required;
- the verified `--enable-argon2=libargon2` build configuration;
- build and runtime dependencies;
- expected RPM subpackages;
- reproducible local `rpmbuild` commands;
- post-install tests for Argon2id, bcrypt, LDAP bind and SSSD integration;
- rollback and package replacement steps.

Do not download unpinned sources or dependencies during the build. Keep
production data, LDAP dumps, credentials, private signing keys and generated
secret material outside this repository.

## Cryptography and password schemes

- Argon2id is the reason for the custom OpenLDAP build.
- OpenLDAP must be built with native Argon2 support using the verified upstream
  build option `--enable-argon2=libargon2` when the dependency and source
  configuration support it.
- Bcrypt does not require a custom OpenLDAP password module for this project.
  Rocky's `libxcrypt` provides bcrypt through the system `crypt(3)` interface,
  consumed by OpenLDAP as `{CRYPT}$2b$...`.
- Do not describe bcrypt as a native OpenLDAP scheme.
- Do not claim Argon2id support until the built RPM is installed and verified
  with reproducible tests in the approved Rocky lab.

## Licensing

The OpenLDAP package uses the upstream OpenLDAP Public License and may include
components with additional upstream licenses. Do not relabel the package as
MIT. MIT may be used for original Candango helper code only if that code is
actually authored and licensed as MIT.

Preserve upstream license files and notices in the resulting packages.

## Deployment model

The custom RPM replaces the distribution OpenLDAP packages on LDAP hosts; two
OpenLDAP versions must not be installed side by side.

Build separately, validate on the approved Rocky lab, preserve artifacts
outside the hosts, and keep a clean rollback path. A snapshot is not an
artifact store.

## Historical state

A previous Rocky-based effort generated an RPM and validated related OpenLDAP
password behavior. The next agent must locate the actual source/spec/artifact
history instead of assuming that a build is reproducible. Rebuild and record
any missing steps.

Known project-level validation requirements:

- OpenLDAP 2.6.10 is the selected observed baseline.
- `{CRYPT}` bcrypt generation through `libxcrypt` must be validated separately.
- Native Argon2id requires the custom OpenLDAP build path and must be tested
  separately.

## Required deliverables

1. Reproducible OpenLDAP source/spec recipe.
2. Explicit Argon2id build configuration and dependency list.
3. RPM build output for Rocky 10 x86_64.
4. Package metadata and preserved licenses.
5. Installation and rollback procedure.
6. Validation covering package installation, Argon2id generation/verification,
   bcrypt compatibility, LDAP bind, and SSSD client behavior.
7. Clear separation between public COPR artifacts and internal production
   repository promotion.

## Security boundaries

- Never commit secrets, private signing keys, LDAP dumps, passwords or tokens.
- Never print passwords in build logs or test output.
- Do not use unreviewed third-party COPR packages as production dependencies.
- Sign release artifacts with a controlled key kept outside the public repo and
  build workers.
- Treat COPR as a public/test distribution path until proven otherwise.
- Production promotion requires a signed artifact, dependency review and
  approved Rocky lab validation.

## Immediate next steps

1. Inspect repository history and existing files.
2. Identify the previous RPM build recipe and source revision.
3. Create or recover the OpenLDAP spec and patches.
4. Build in COPR with the Rocky 10-compatible EPEL chroot.
5. Install and validate the result in the approved Rocky lab.
6. Record exact commands, versions, hashes and test results without exposing
   credentials or generated password hashes.
