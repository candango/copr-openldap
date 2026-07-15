# Agent Instructions

Read `CONTEXT.md` completely before changing this repository. Local operator
lab details, access instructions and transient host evidence belong only in
`LAB_INFO.md`, which is ignored by Git.

## Scope

This repository owns the Candango OpenLDAP COPR packaging and validation work.
It does not own production LDAP data or host configuration.

## Rules

- Keep persistent documentation, task descriptions and commit messages in
  English.
- Do not commit secrets, private keys, credentials, LDAP dumps or generated
  secret material.
- Preserve upstream OpenLDAP license notices.
- Use the OpenLDAP Public License for the upstream package; do not mark the
  package MIT.
- Keep Argon2id and bcrypt claims technically distinct:
  Argon2id is the custom OpenLDAP build feature; bcrypt is provided through
  Rocky `libxcrypt` and OpenLDAP `{CRYPT}`.
- Prefer reproducible, pinned source inputs with checksums.
- Do not enable arbitrary network access in COPR builds.
- Do not promote a COPR artifact to production without approved Rocky lab
  validation.
- Do not overwrite or delete existing work without inspecting Git state first.
- Before committing, inspect the staged diff and run the relevant build/tests.
- Never include credentials or private signing material in logs, artifacts or
  commits.
- Keep hostnames, IP addresses, SSH commands, key paths and transient lab
  evidence out of tracked documentation; store them only in local
  `LAB_INFO.md`.

## First action for a new agent

1. Read `CONTEXT.md` completely.
2. Inspect `git status`, repository history and existing packaging files.
3. Locate the previous RPM/spec/build evidence.
4. Report findings before making broad design changes.
