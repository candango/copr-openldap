Name:           openldap
Version:        2.6.10
Release:        2%{?dist}.candango
Summary:        OpenLDAP server and client with native Argon2id support

License:        OpenLDAP Public License
URL:            https://www.openldap.org/
Source0:        https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-%{version}.tgz
Source1:        slapd.sysconfig

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  openssl-devel
BuildRequires:  cyrus-sasl-devel
BuildRequires:  libargon2-devel
BuildRequires:  libxcrypt-devel
BuildRequires:  lmdb-devel
BuildRequires:  systemd-devel


%description
OpenLDAP directory server and client libraries for Rocky Linux 10. This
Candango build enables and validates native Argon2id password support. Bcrypt
remains provided by the system libxcrypt implementation through OpenLDAP's
CRYPT password scheme.

%package clients
Summary:        OpenLDAP client utilities

%description clients
Client utilities for querying and managing OpenLDAP directories.

%package devel
Summary:        Development files for OpenLDAP
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers, static libraries, pkg-config metadata and manual pages for
building software against OpenLDAP.

%package servers
Summary:        OpenLDAP directory server
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description servers
The OpenLDAP directory server and its service files.

%prep
%autosetup -p1

%build
# Keep published binaries compatible with the Rocky x86_64_v2 baseline.
CFLAGS=$(printf '%s\n' "$CFLAGS" | sed 's/-march=x86-64-v3/-march=x86-64-v2/g')
CXXFLAGS=$(printf '%s\n' "$CXXFLAGS" | sed 's/-march=x86-64-v3/-march=x86-64-v2/g')
export CFLAGS CXXFLAGS

%configure \
    --with-tls=openssl \
    --with-cyrus-sasl \
    --enable-argon2 \
    --with-argon2=libargon2 \
    --enable-crypt \
    --enable-dynamic \
    --enable-modules \
    --enable-slapd \
    --disable-sql
%make_build

%install
%make_install
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/slapd

%post servers
%systemd_post slapd.service

%preun servers
%systemd_preun slapd.service

%postun servers
%systemd_postun_with_restart slapd.service

%check
%make_build test

# LICENSE and COPYRIGHT are supplied by the upstream OpenLDAP source archive.
# The repository's MIT LICENSE is not included in the RPM.
%files
%license LICENSE COPYRIGHT
%doc README
%{_libdir}/liblber.so.2*
%{_libdir}/libldap.so.2*

%files clients
%license LICENSE COPYRIGHT
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man5/ldap.conf.5*

%files devel
%license LICENSE COPYRIGHT
%{_includedir}/*.h
%{_libdir}/*.a
%{_libdir}/liblber.so
%{_libdir}/libldap.so
%{_libdir}/pkgconfig/*.pc
%{_mandir}/man3/*

%files servers
%license LICENSE COPYRIGHT
%{_sbindir}/*
%{_libexecdir}/slapd
%{_libexecdir}/openldap/
%{_sysconfdir}/openldap/
%config(noreplace) %{_sysconfdir}/sysconfig/slapd
%{_unitdir}/slapd.service
%{_mandir}/man5/ldif.5*
%{_mandir}/man5/lloadd.conf.5*
%{_mandir}/man5/slapd*.5*
%{_mandir}/man5/slapo-*.5*
%{_mandir}/man5/slappw-argon2.5*
%{_mandir}/man8/*

%changelog
* Tue Jul 14 2026 Candango Packaging <packages@candango.org> - 2.6.10-1.candango
- Scaffold the Rocky Linux 10 Argon2id-enabled OpenLDAP package.
