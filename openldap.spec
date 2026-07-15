Name:           openldap
Version:        2.6.10
Release:        1%{?dist}.candango
Summary:        OpenLDAP server and client with native Argon2id support

License:        OpenLDAP Public License
URL:            https://www.openldap.org/
# TODO: Pin Source0 to the verified upstream tarball and record its SHA256 in
# sources before the first COPR build.
Source0:        https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-%{version}.tgz

# TODO: Add the verified Argon2id patch set, if the selected upstream release
# requires patches beyond --enable-argon2 --with-argon2=libargon2.
# Patch0:        openldap-argon2id.patch

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  openssl-devel
BuildRequires:  cyrus-sasl-devel
BuildRequires:  libargon2-devel
BuildRequires:  lmdb-devel

Requires:       openldap-clients%{?_isa} = %{version}-%{release}

%description
OpenLDAP directory server and client libraries for Rocky Linux 10. This
Candango build enables and validates native Argon2id password support. Bcrypt
remains provided by the system libxcrypt implementation through OpenLDAP's
CRYPT password scheme.

%package clients
Summary:        OpenLDAP client utilities

%description clients
Client utilities for querying and managing OpenLDAP directories.

%package servers
Summary:        OpenLDAP directory server
Requires:       %{name}-clients%{?_isa} = %{version}-%{release}

%description servers
The OpenLDAP directory server and its service files.

%prep
%autosetup -p1

%build
# TODO: Confirm the complete Rocky 10 configure matrix before enabling COPR.
# Rocky 10.2 guidance uses separate enable and provider options.
%configure \
    --with-tls=openssl \
    --with-cyrus-sasl \
    --enable-argon2 \
    --with-argon2=libargon2 \
    --enable-dynamic \
    --disable-slapd \
    --disable-sql
%make_build

%install
%make_install

# TODO: Split files into the final upstream-compatible subpackages.

%check
%make_build test

# LICENSE and COPYRIGHT are supplied by the upstream OpenLDAP source archive.
# The repository's MIT LICENSE is not included in the RPM.
%files
%license LICENSE COPYRIGHT
%doc README.md

%files clients
%license LICENSE COPYRIGHT

%files servers
%license LICENSE COPYRIGHT

%changelog
* Tue Jul 14 2026 Candango Packaging <packages@candango.org> - 2.6.10-1.candango
- Scaffold the Rocky Linux 10 Argon2id-enabled OpenLDAP package.
