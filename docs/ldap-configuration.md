# LDAP Configuration and Validation

This document describes the generic OpenLDAP password, SSSD and PAM
configuration model. Hostnames, endpoints, access instructions and transient
validation evidence are intentionally kept outside Git.

## Password scheme model

| Scheme | Where it is provided | Use in this project |
|---|---|---|
| `{ARGON2}` | OpenLDAP Argon2 password module loaded by `slapd` | Preferred server-side default |
| `{CRYPT}$2b$...` | Rocky `libxcrypt` through `crypt(3)` | Bcrypt compatibility/fallback |
| `{SSHA}` | OpenLDAP built-in `slappasswd` support | Compatibility only |
| `{SHA}`, `{SMD5}`, `{MD5}` | OpenLDAP built-in support | Legacy compatibility only; do not select for new passwords |

`{ARGON2ID}` and `{BCRYPT}` are not separate scheme names for this project.
Do not invent scheme names in LDAP configuration.

## Configure the server default

The dynamic configuration attribute is:

```text
olcPasswordHash: {ARGON2}
```

It belongs under the intended `cn=config` database entry. The legacy static
configuration equivalent is:

```text
password-hash {ARGON2}
```

Use `cn=config` for Rocky 10 deployments. Apply changes through an
authenticated LDAPI operation with a reviewed LDIF, then verify the resulting
attribute. Do not edit generated files under `slapd.d` directly.

Example LDIF shape (review the target DN before applying):

```ldif
dn: olcDatabase={-1}frontend,cn=config
changetype: modify
replace: olcPasswordHash
olcPasswordHash: {ARGON2}
```

## `slappasswd`

`slappasswd` chooses a scheme explicitly. It does not inherit
`olcPasswordHash` from the running server:

```bash
slappasswd -h '{SSHA}'
slappasswd -h '{CRYPT}'
```

Do not put real passwords on the command line. Prefer an interactive prompt or
an approved secret-handling mechanism. Never commit generated hashes for real
users.

For bcrypt through `libxcrypt`, request the bcrypt format through `CRYPT` and
verify that the result begins with `{CRYPT}$2b$`. There is no separate
`{BCRYPT}` scheme in this OpenLDAP path.

For standalone Argon2 generation, explicitly load the server module:

```bash
slappasswd -o module-load=argon2 -h '{ARGON2}'
```

## Server-side password change

Use LDAP Password Modify over protected LDAP transport so the server applies
its configured password scheme:

```bash
ldappasswd \
  -H ldaps://ldap.example.test:636 \
  -D 'uid=<admin>,ou=People,dc=example,dc=test' \
  -W \
  'uid=<user>,ou=People,dc=example,dc=test'
```

Use certificate validation in real tests. Do not disable TLS verification.
Passwords must be obtained interactively or through an approved secret path,
never through shell arguments or logs.

After changing a disposable validation user's password, validate authentication
with a user bind over protected LDAP transport. Do not retrieve or display the
stored hash.

## SSSD and PAM

Production client transport should use protected LDAP:

```ini
ldap_uri = ldaps://ldap.example.test:636
ldap_id_use_start_tls = false
ldap_tls_reqcert = demand
```

Use a CA trusted by the client. Do not configure StartTLS on an `ldaps://` URI.
StartTLS is an alternative only with `ldap://...:389`,
`ldap_id_use_start_tls = true`, and server/firewall enforcement against
plaintext binds.

On Rocky Linux, use `authselect` rather than hand-editing generated PAM files:

```bash
sudo authselect select sssd with-mkhomedir --force
sudo systemctl enable --now oddjobd sssd
sudo sssctl config-check
sudo systemctl restart sssd
```

Keep technical bind credentials in an approved local secret path. Do not commit
SSSD secrets or generated password files to this repository.

Validate lookup and authentication interactively:

```bash
getent passwd <ldap-user>
id <ldap-user>
sudo sssctl user-checks <ldap-user>
su - <ldap-user>
```

Verify UID/GID ownership and home creation without printing credentials.

## Validation boundary

The minimum validation sequence is:

1. confirm package version, provenance and loaded Argon2 module;
2. confirm `olcPasswordHash: {ARGON2}` without exposing hashes;
3. change a disposable user's password through LDAP Password Modify over
   protected transport;
4. authenticate with a user bind over protected LDAP;
5. validate `getent`, `id`, SSSD checks and interactive PAM login;
6. validate `{CRYPT}$2b$` bcrypt compatibility separately;
7. record versions, package provenance and test results without secrets;
8. restore the approved clean validation state when the test cycle is complete.

A successful server test does not prove that the Candango COPR RPM was used.
Record `rpm -q`, package repository provenance and the build identifier.
