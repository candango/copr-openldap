# Candango OpenLDAP COPR

Packaging scaffold for the `candango/openldap` COPR project.

This project targets Rocky Linux 10 and exists to build OpenLDAP with validated
native Argon2id support. Bcrypt remains provided by Rocky's `libxcrypt`
implementation through OpenLDAP's `{CRYPT}` scheme.

## Status

The RPM recipe is scaffolding and is **not ready for deployment**. Resolve the
TODOs in `openldap.spec` and `sources` before building or publishing packages.

Read these files first:

- [`AGENTS.md`](AGENTS.md) — agent operating rules;
- [`CONTEXT.md`](CONTEXT.md) — project context and decisions;
- [`docs/build.md`](docs/build.md) — build and validation workflow;
- [`docs/ldap-configuration.md`](docs/ldap-configuration.md) — OpenLDAP,
  `slappasswd`, SSSD and PAM configuration and validation.

Local operator infrastructure and lab access details belong in the ignored
`LAB_INFO.md`; they are not part of the tracked project documentation.

## License

The packaging repository's original files are MIT-licensed. The OpenLDAP
software retains its upstream OpenLDAP Public License and other applicable
upstream notices.
