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
BuildRequires: hipercontracer-libhipercontracer-devel
BuildRequires: boost-devel
BuildRoot: %{_tmppath}/%{name}-%{version}-build


# This package does not generate debug information (no executables):
# %global debug_package %{nil}

# TEST ONLY:
# define _unpackaged_files_terminate_build 0


%description
NorNet is a testbed for multi-homed systems. This package
contains the Atlas/MNS Trace experiment scripts.
See https://www.nntb.no for details on NorNet!

%prep
%setup -q

%build
%cmake -DCMAKE_INSTALL_PREFIX=/usr .
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install



%package scheduler
Summary: Atlas/MNS Trace Scheduler
Group: Applications/Internet
BuildArch: noarch
Requires: nornet-management
Requires: python3-psycopg2
Requires: python3-pymongo

%description scheduler
 Atlas/MNS Trace Scheduler is the scheduler for the Atlas/MNS Trace experiments.
 See https://www.nntb.no for details on NorNet!

%files scheduler
/usr/lib/python*/*-packages/AtlasMNS*.egg-info
/usr/lib/python*/*-packages/AtlasMNS.py
/usr/lib/python*/*-packages/__pycache__/AtlasMNS*.pyc
%{_bindir}/atlasmns-trace-scheduler
%{_mandir}/man1/atlasmns-trace-scheduler.1.gz
%{_datadir}/doc/atlasmns-trace/examples/atlasmns-database-configuration
%{_datadir}/doc/atlasmns-trace/examples/SQL/README
%{_datadir}/doc/atlasmns-trace/examples/SQL/database.sql
%{_datadir}/doc/atlasmns-trace/examples/SQL/install-database-and-users
%{_datadir}/doc/atlasmns-trace/examples/SQL/schema.sql
%{_datadir}/doc/atlasmns-trace/examples/SQL/users.sql
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/admin.ms
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/database.ms
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/install-database-and-users
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/schema.ms
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/users.ms
%{_datadir}/doc/atlasmns-trace/examples/NoSQL/README


%package agent
Summary: Atlas/MNS Trace Agent
Group: Applications/Internet
BuildArch: noarch
Requires: hipercontracer >= 1.4.0
Requires: nornet-trace-trigger
Requires: python3-psycopg2
Requires: python3-pymongo

%description agent
 Atlas/MNS Trace Agent is the agent for the Atlas/MNS Trace experiments.
 See https://www.nntb.no for details on NorNet!

%files agent
%{_bindir}/atlasmns-trace-agent
%{_mandir}/man1/atlasmns-trace-agent.1.gz



%changelog
* Fri Jun 14 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
