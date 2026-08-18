#!/usr/bin/env bash
set -euo pipefail

# This test is intentionally non-destructive. It validates the local package
# metadata and becomes the entry point for Rocky lab integration checks.

command -v rpmspec >/dev/null || {
    printf '%s\n' 'rpmspec is required for package validation' >&2
    exit 1
}

rpmspec -P openldap.spec >/dev/null
printf '%s\n' 'RPM spec validation passed'

for source in openldap.sysusers slapd.tmpfiles slapd.ldif; do
    test -f "$source" || {
        printf 'missing packaging input: %s\n' "$source" >&2
        exit 1
    }
done

grep -q '^g[[:space:]]\+ldap[[:space:]]\+55$' openldap.sysusers
grep -q '^u[[:space:]]\+ldap[[:space:]]\+55:55' openldap.sysusers
grep -q '^d /run/openldap 0755 ldap ldap -$' slapd.tmpfiles
grep -q '^olcDbDirectory: /var/lib/ldap$' slapd.ldif
! grep -q '^olcRootPW:' slapd.ldif
printf '%s\n' 'Bootstrap packaging inputs validated'

# TODO: Add post-build checks for:
# - native Argon2id generation and verification;
# - {CRYPT}$2b$ bcrypt compatibility through libxcrypt;
# - LDAP bind and slapd startup in the approved validation environment;
# - SSSD lookup/authentication from the approved client environment.
