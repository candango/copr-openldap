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

# TODO: Add post-build checks for:
# - native Argon2id generation and verification;
# - {CRYPT}$2b$ bcrypt compatibility through libxcrypt;
# - LDAP bind and slapd startup in the approved validation environment;
# - SSSD lookup/authentication from the approved client environment.
