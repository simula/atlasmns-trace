Name: atlasmns-trace
Version: 0.0.0
Release: 1
Summary: NorNet Control
Group: Applications/Internet
License: GPLv3
URL: https://www.nntb.no/
Source: https://packages.nntb.no/software/%{name}/%{name}-%{version}.tar.xz

AutoReqProv: on
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRoot: %{_tmppath}/%{name}-%{version}-build


# This package does not generate debug information (no executables):
%global debug_package %{nil}

# TEST ONLY:
# define _unpackaged_files_terminate_build 0


%description
NorNet is a testbed for multi-homed systems. This package
contains the NorNet Trace serice scripts.
See https://www.nntb.no for details on NorNet!

%prep
%setup -q

%build
%cmake -DCMAKE_INSTALL_PREFIX=/usr .
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install



%package importer
Summary: NorNet Trace Importer
Group: Applications/Internet
BuildArch: noarch
Requires: crontabs
Requires: hipercontracer
Requires: atlasmns-management

%description importer
 NorNet Trace Importer is the importer cron job to import results from the
 NorNet Trace Service into a database.
 See https://www.nntb.no for details on NorNet!

%files importer
%config(noreplace) %{_sysconfdir}/cron.d/atlasmns-trace-importer



%package service
Summary: NorNet Trace Service
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-importer = %{version}-%{release}
Requires: hipercontracer
Requires: atlasmns-tunnelbox

%description service
 NorNet Trace Service is the traceroute service for the NorNet testbed.
 It performs regular HiPerConTracer runs among all sites.
 See https://www.nntb.no for details on NorNet!

%files service
%{_bindir}/nornetinfogenerator
%{_mandir}/man1/nornetinfogenerator.1.gz



%changelog
* Thu Jun 14 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
