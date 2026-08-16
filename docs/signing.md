# RPM signing and repository metadata

This runbook signs the Candango RPMs and the repository metadata for the
Rocky Linux 10 x86_64_v2 repository. Run it from the repository root, where
the distributed RPMs and `repodata/` are located.

## Security requirements

- Use the protected signing workstation and the approved Candango signing key.
- Keep the private key and its `GNUPGHOME` outside this Git repository.
- Do not place passphrases, private keys, or generated secret material in the
  command line, logs, artifacts, or commits.
- Do not sign or publish artifacts that have not passed the Rocky lab release
  gates.
- The `.repo` client configuration does not need a GPG signature; serve it
  over HTTPS and keep `gpgcheck=1` and `repo_gpgcheck=1` enabled.

The actual protected GnuPG home is operator-local and must be supplied outside
tracked documentation. For example:

```bash
export GNUPGHOME=/path/to/protected/candango-gnupg
export SIGNING_KEY="<approved-signing-key-fingerprint>"
```

Confirm that the selected public key has the approved fingerprint before
signing:

```bash
gpg --list-keys --with-fingerprint "$SIGNING_KEY"
```

## Required order

The order is intentional. Package signatures must exist before repository
metadata is generated, and the metadata signature must be created last.

### 1. Select the package set

Run this from the repository root. The glob must include every RPM that will
be distributed, including debug packages and a source RPM if the source RPM is
part of the published set.

```bash
set -euo pipefail

packages=(./*.rpm)
((${#packages[@]} > 0)) || {
  printf '%s\n' 'No RPMs found in the repository root.' >&2
  exit 1
}
```

Remove or move stale and unsigned packages before continuing. Do not leave
multiple releases of the same package in the published root.

### 2. Sign every distributed RPM

Use the approved key explicitly. `rpmsign` may invoke the protected GPG agent
for the key passphrase; do not provide that passphrase on the command line.

```bash
for pkg in "${packages[@]}"; do
  rpmsign --addsign \
    --define "%_gpg_name ${SIGNING_KEY}" \
    "$pkg"
done
```

### 3. Verify every RPM signature

Every package must report a valid OpenPGP signature, header digest, and payload
digest.

```bash
for pkg in "${packages[@]}"; do
  rpm --checksig -v "$pkg"
done
```

Stop if any package fails. Do not generate or sign repository metadata for a
partially verified package set.

### 4. Generate repository metadata

After the package signatures pass, generate or update the repository metadata:

```bash
createrepo_c --update .
```

If this is a new repository with no existing metadata, use `createrepo_c .`
instead. Any package addition, removal, replacement, or metadata regeneration
requires the metadata signature to be recreated.

### 5. Sign `repomd.xml`

Sign the freshly generated metadata with the same approved repository key:

```bash
gpg --armor \
  --local-user "$SIGNING_KEY" \
  --detach-sign repodata/repomd.xml
```

This creates:

```text
repodata/repomd.xml.asc
```

### 6. Verify the metadata signature

```bash
gpg --verify repodata/repomd.xml.asc repodata/repomd.xml
```

The result must identify the approved signing key and report `Good signature`.

## Final release checks

Before publication, confirm that the repository contains only the approved
release and that the files are in the expected root:

```bash
find . -maxdepth 1 -type f -name '*.rpm' -printf '%f\n' | sort
sha256sum ./*.rpm repodata/repomd.xml repodata/repomd.xml.asc
```

Publish the repository root together with `repodata/`, the public key, and the
client `.repo` file. Do not publish the private key or the protected
`GNUPGHOME`.

On a clean Rocky client, configure the repository with both package and
metadata verification enabled:

```ini
gpgcheck=1
repo_gpgcheck=1
```

Validate that DNF selects `1.el10_2_1.candango` over EPEL `1.el10_2`, then
run the approved OpenLDAP installation and runtime tests before distributing
through Ansible.
