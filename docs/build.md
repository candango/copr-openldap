# Build Workflow

## Local preparation

1. Read `CONTEXT.md` and `AGENTS.md`.
2. Confirm the OpenLDAP upstream version and source checksum.
3. Confirm the Argon2id patch/configuration against the selected upstream
   release.
4. Keep secrets, signing keys and local infrastructure details outside this
   repository.

Local operator infrastructure and approved validation endpoints, when needed,
are documented outside Git in `LAB_INFO.md`.

## Local RPM build

```bash
make spec-check
make build
```

The current spec is scaffolding. Do not publish or deploy it until the TODOs
in `openldap.spec` and `sources` are resolved.

## COPR

Project:

```text
candango/openldap
```

Target chroot:

```text
alma+epel-10-x86_64_v2
```

Keep internet access disabled. All source inputs must be declared and pinned.

## Validation

Install the resulting package only in an approved disposable Rocky validation
environment. Run non-destructive package checks first, preserve artifacts
outside the validation hosts, and retain a clean rollback path.

The validation must cover package provenance, Argon2id generation and
verification, bcrypt compatibility through `{CRYPT}`, LDAP bind over protected
transport, and SSSD/PAM integration. Do not print credentials, directory
password values or generated user hashes.
