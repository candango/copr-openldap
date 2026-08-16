# OpenLDAP Build and Validation Runbook

This runbook describes the complete path from a clean Rocky Linux 10 machine to
an inspected and validated RPM set. It applies only to disposable build and
validation environments. It does not describe production deployment.

The process has four gates:

1. the machine baseline is known and reproducible;
2. the source and spec inputs are pinned and pass static checks;
3. the RPMs build and package metadata is correct;
4. the installed RPMs pass the password, LDAP and SSSD validation.

Do not skip a gate or promote an artifact that has not passed all four.

## 1. Restore and record the machine baseline

1. Restore the approved clean Rocky Linux 10 snapshot using the provider's
   documented procedure.
2. Confirm that the machine is disposable and is not a production LDAP host.
3. Record the Rocky release, architecture, kernel, enabled repositories and
   snapshot identifier in local operator evidence. Keep hostnames, addresses,
   access instructions and transient evidence in the ignored `LAB_INFO.md`,
   never in tracked documentation.
4. Do not delete LDAP data or remove packages manually as a substitute for the
   approved snapshot restore.

Initial checks:

```bash
cat /etc/rocky-release
uname -m
uname -r
lscpu
nproc
free -h
lsblk
dnf repolist
```

Use `lscpu` to inspect the architecture, model, virtualisation provider, CPU
count and exposed instruction flags. `nproc`, `free -h` and `lsblk` show the
resources available to the build or validation machine. Record the relevant
output in local evidence, not tracked documentation, when it contains host-
specific details.

The expected target is Rocky Linux 10 x86_64. Stop if the release or
architecture is different.

### x86-64 microarchitecture baseline

`x86-64-v2` and `x86-64-v3` are CPU instruction-set levels, not OpenLDAP or
RPM versions. The original x86-64 baseline is the most compatible. v2 adds
instructions such as SSE3, SSSE3, SSE4.1, SSE4.2, `POPCNT`, `CMPXCHG16B` and
`LAHF/SAHF`. v3 adds newer instructions including AVX, AVX2, FMA, BMI1 and
BMI2.

A binary built for a level may execute those instructions. Running a v3 binary
on a CPU that only supports v2 can fail with `Illegal instruction`; choosing a
higher level can improve performance but reduces the compatible hardware
fleet. This project uses v2 because the approved Rocky build baseline requires
x86_64_v2 while retaining broader compatibility than v3. The RPM architecture
still remains `x86_64`; `x86_64_v2` identifies the repository/build baseline.

Check the CPU level on the build or validation machine:

```bash
/lib64/ld-linux-x86-64.so.2 --help | grep -E 'x86-64-v[234]'
```

`x86-64-v2 (supported, searched)` confirms v2 support. A line without
`(supported, searched)` does not confirm support. If the dynamic loader path is
different, locate the host's x86-64 loader before running the check. The
following command exposes the individual CPU flags when a detailed check is
needed:

```bash
grep -m1 '^flags' /proc/cpuinfo
```

The v2 check validates the machine, not the RPM. The build must separately
record `-march=x86-64-v2` (and matching `CFLAGS`/`CXXFLAGS`) in the build log or
configuration evidence. Do not infer the artifact baseline only from the CPU
that built it.

## 2. Prepare the Rocky build machine

Enable the repositories required by the local Rocky environment. EPEL is
needed for `libargon2-devel`; CRB is needed for `lmdb-devel` when those
packages are not already available:

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --set-enabled crb
sudo dnf install -y epel-release
sudo dnf makecache
```

Keep EPEL enabled because it supplies the Argon2 build and runtime packages.
Do not disable EPEL globally. The Candango repository owns the OpenLDAP
packages, so exclude EPEL's competing OpenLDAP package names on validation and
consumer hosts:

```ini
# /etc/yum.repos.d/epel.repo, in the [epel] section
excludepkgs=openldap*
```

The wildcard also covers `openldap-servers`, `openldap-slapi`,
`openldap-slapi-compat` and `openldap-slapi-devel`. This prevents a leftover
EPEL OpenLDAP package from being selected while allowing EPEL to provide
`libargon2` and other unrelated dependencies. Remove any conflicting
OpenLDAP packages already installed on a disposable host before the first
Candango installation; an exclusion does not remove an installed package.

Install the RPM toolchain and the dependencies declared by the spec:

```bash
sudo dnf install -y \
  rpm-build rpmdevtools redhat-rpm-config \
  gcc gcc-c++ make autoconf automake libtool \
  pkgconf-pkg-config openssl-devel cyrus-sasl-devel \
  libargon2-devel lmdb-devel
```

Create the per-user RPM build tree and verify the tools:

```bash
rpmdev-setuptree
command -v rpmspec rpmbuild gcc make
rpm --eval '%{_target_cpu}'
```

The preparation can be executed from a Fedora control node with the
repository's Ansible playbook. The target needs only SSH access, Python and
sudo; Ansible, Go and this source tree remain on the control node:

```bash
ansible-playbook \
  -i '<build-host>,' \
  -u '<build-user>' \
  --private-key '<ssh-key>' \
  -e build_user='<build-user>' \
  ansible/prepare-rocky-build.yml
```

The inline inventory keeps the target out of tracked repository data. The
Rocky host and its approved repositories must already be prepared. The pinned
OpenLDAP archive must already exist in the remote user's `rpmbuild/SOURCES`
directory. The playbook validates Rocky Linux 10 x86_64 and x86-64-v2, installs
the declared OpenLDAP build dependencies, initializes the remote user's RPM
tree, stages the spec and Candango sources, and verifies the upstream archive
against `sources`. It does not download or transfer the upstream archive, run
`rpmbuild`, install OpenLDAP, sign artifacts, or configure the public Candango
repository.

Use only approved Rocky repositories for build dependencies. Do not add
unreviewed COPR repositories, download dependencies during `%build`, or place
credentials and private signing keys on the build host.

## 3. Obtain and verify the repository

Use the approved repository revision. Do not build from an uncommitted working
 tree or from unreviewed local changes:

```bash
git clone <approved-repository-url> copr-openldap
cd copr-openldap
git checkout <approved-revision>
git status --short --branch
git log -n 1 --oneline
```

Read `CONTEXT.md` and `AGENTS.md` before changing anything. Inspect the spec,
`patches/`, `sources` and tests:

```bash
sed -n '1,240p' openldap.spec
cat sources
find patches tests docs -maxdepth 2 -type f -print | sort
```

Do not continue while `openldap.spec` or `sources` contains unresolved source,
configuration, packaging or licensing TODOs.

## 4. Verify source inputs

The spec must identify the exact OpenLDAP release and every source or patch.
The `sources` file must contain the verified SHA256 for the upstream archive.
Download sources only through the approved source process, then verify them
before the RPM build:

```bash
sha256sum <downloaded-openldap-archive>
# Compare the result with the pinned value in sources.
```

Keep the upstream OpenLDAP license notices in the source archive and resulting
RPMs. The repository's MIT license applies only to original Candango helper
material; it does not change the OpenLDAP package license.

## 5. Run static checks

Run these checks from the repository root:

```bash
make spec-check
bash ./tests/validate-package.sh
```

Review the preprocessed spec and ensure that it has the expected subpackages,
BuildRequires, configure flags and `%files` entries:

```bash
rpmspec -P openldap.spec > /tmp/openldap.spec.preprocessed
less /tmp/openldap.spec.preprocessed
```

The build configuration must enable the verified native Argon2 provider,
including the approved `--enable-argon2=libargon2` form when supported by the
selected upstream release. Do not describe bcrypt as native OpenLDAP support:
Rocky `libxcrypt` provides bcrypt through `{CRYPT}`.

## 6. Build the RPMs

Build from the pinned inputs with the standard RPM tree:

```bash
make build
```

If the build is run without the Makefile target, use:

```bash
rpmbuild -ba openldap.spec
```

For the approved v2 baseline, preserve the effective compiler flags and the
build log as evidence. Confirm that the build did not silently inherit a
stronger host-specific setting such as `-march=x86-64-v3`; a successful build
on a v3 machine does not prove v2 compatibility.

Do not fix build failures by adding network downloads to `%build` or `%install`.
Resolve missing inputs in the spec, sources or machine preparation instead.
Preserve the complete build log and the source/checksum evidence outside the
repository and outside the validation host.

## 7. Inspect the artifacts before installation

List and inspect every generated package:

```bash
find "$HOME/rpmbuild/RPMS" "$HOME/rpmbuild/SRPMS" -type f -print
rpm -qip "$HOME"/rpmbuild/RPMS/*/openldap-*.rpm
rpm -qlp "$HOME"/rpmbuild/RPMS/*/openldap-*.rpm
rpm -qp --requires "$HOME"/rpmbuild/RPMS/*/openldap-*.rpm
rpm -qp --provides "$HOME"/rpmbuild/RPMS/*/openldap-*.rpm
```

Confirm the following before installation:

- the version and release match the approved source revision;
- server and client subpackages are present and have coherent dependencies;
- the service files, modules, configuration files and binaries are owned by a
  package;
- the upstream license and notices are present;
- no private key, credential, dump or generated secret is present;
- the package does not silently replace unrelated system files.

Copy RPMs, SRPMs, checksums and logs to an approved artifact store before
restoring or reusing the validation machine. A VM snapshot is not an artifact
store.

## 8. Install on the disposable validation machine

Install the locally built packages only after the artifact inspection passes:

```bash
sudo dnf install -y ./RPMS/*/openldap-*.rpm
rpm -qa 'openldap*' 'libargon2*' 'libxcrypt*'
rpm -qf /usr/sbin/slapd /usr/bin/slappasswd
```

Do not install a second OpenLDAP distribution beside the custom package. If a
pre-existing OpenLDAP installation is present, record its provenance and use
the approved replacement or rollback procedure.

Configure only disposable test data and reviewed test identities. Never copy
production LDAP data or credentials into the validation environment. Start and
enable `slapd` only after reviewing its generated configuration and service
unit:

```bash
systemctl cat slapd
sudo systemctl enable --now slapd
systemctl --no-pager --full status slapd
```

## 9. Run functional validation

Validation must prove the custom RPM was used and must not expose password
values or stored hashes:

```bash
rpm -q openldap openldap-servers openldap-clients
slappasswd -o module-load=argon2 -h '{ARGON2}'
slappasswd -h '{CRYPT}'
```

Use interactive or approved secret handling for those commands. Confirm the
Argon2 module loads and the result uses `{ARGON2}`. Confirm bcrypt separately
through `{CRYPT}$2b$...`; there is no native `{BCRYPT}` OpenLDAP scheme.

Complete the lab validation with a disposable directory and protected LDAP
transport:

1. verify the configured `{ARGON2}` default without reading `userPassword`;
2. change a disposable user's password through LDAP Password Modify;
3. authenticate with a user bind over protected LDAP;
4. validate `{CRYPT}` bcrypt compatibility separately;
5. validate `getent`, `id`, `sssctl user-checks` and PAM/SSSD login on the
   approved client host;
6. record package versions, provenance and pass/fail results without recording
   credentials or generated hashes.

Use `docs/ldap-configuration.md` for the protected transport and SSSD
configuration rules. Never disable certificate verification in the validation
path.

## 10. Roll back and preserve evidence

After validation, preserve artifacts and evidence outside the host, then use
the approved clean snapshot to restore the validation machine. Do not use
ad-hoc package deletion as rollback.

If an immediate package rollback is required before snapshot restoration, stop
services and use the approved package replacement procedure. Never leave two
OpenLDAP versions installed side by side.

Record the exact source revision, source SHA256, RPM NEVRA values, build log,
validation results and snapshot restore result. Do not commit credentials,
private keys, LDAP dumps, password values, generated hashes or transient host
access details.

## Internal RPM release gate

The published repository target is:

```text
rocky/10/x86_64_v2
```

Follow [the RPM signing runbook](signing.md) to sign every distributed RPM,
generate repository metadata, sign `repomd.xml`, and verify both package and
metadata signatures. Only publish after the pinned source checksum, artifact
inspection and approved Rocky lab validation pass. Signing keys remain outside
the repository and build workers. Production distribution through Ansible
requires separate signed release evidence and approval.

The historical COPR target was `alma+epel-10-x86_64_v2`; it remains relevant
only to reproduce the original packaging environment, not as the publication
path.
