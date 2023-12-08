Name: atlasmns-trace
Version: 0.4.10
Release: 1
Summary: AtlasMNS Trace
Group: Applications/Internet
License: GPL-3+
URL: https://www.nntb.no/
Source: https://packages.nntb.no/software/%{name}/%{name}-%{version}.tar.xz

AutoReqProv: on
BuildRequires: boost-devel
BuildRequires: cmake
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: hipercontracer-libhipercontracer-devel >= 1.4.6
BuildRequires: libpqxx-devel
BuildRequires: python3-colorlog
BuildRequires: python3-devel
BuildRequires: python3-psycopg2
BuildRequires: python3-pymongo
BuildRoot: %{_tmppath}/%{name}-%{version}-build


# TEST ONLY:
# define _unpackaged_files_terminate_build 0


%description
This package contains the Atlas/MNS Trace experiment software.
It is used to perform Traceroute experiments between Internet
hosts and RIPE Atlas nodes, based on the HiPerConTracer
library and results importer script. The results are imported
into a MongoDB database for later analysis.

%prep
%setup -q

%build
%cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_LIBRARY_PREFIX=%{buildroot}/usr .
%cmake_build

%install
%cmake_install



%package common
Summary: Atlas/MNS Trace common functions
Group: Applications/Internet
BuildArch: noarch
Requires: nornet-management
Requires: python3-colorlog
Requires: python3-psycopg2
Requires: python3-pymongo
Requires: ripe.atlas.cousteau

%description common
This package contains common functions for the Atlas/MNS Trace programs.
See https://www.nntb.no for details on NorNet!

%files common
%{python3_sitelib}/AtlasMNS*.egg-info
%{python3_sitelib}/AtlasMNS.py
%{python3_sitelib}/AtlasMNSLogger.py
%{python3_sitelib}/AtlasMNSTools.py
%{python3_sitelib}/__pycache__/AtlasMNS*.pyc
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


%package controller
Summary: Atlas/MNS Trace Controller
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-common = %{version}-%{release}

%description controller
 Atlas/MNS Trace Controller is the controller for the Atlas/MNS Trace experiments.
 See https://www.nntb.no for details on NorNet!

%files controller
%{_bindir}/atlasmns-trace-controller
%{_mandir}/man1/atlasmns-trace-controller.1.gz


%package scheduler
Summary: Atlas/MNS Trace Scheduler
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-common = %{version}-%{release}

%description scheduler
Atlas/MNS Trace Scheduler is the scheduler for the Atlas/MNS Trace experiments.
See https://www.nntb.no for details on NorNet!

%files scheduler
%{_bindir}/atlasmns-trace-scheduler
%{_mandir}/man1/atlasmns-trace-scheduler.1.gz


%package agent
Summary: Atlas/MNS Trace Agent
Group: Applications/Internet
Requires: hipercontracer >= 1.4.6
Requires: %{name}-common = %{version}-%{release}

%description agent
Atlas/MNS Trace Agent is the agent for the Atlas/MNS Trace experiments.
See https://www.nntb.no for details on NorNet!

%files agent
%{_bindir}/atlasmns-trace-agent
%{_mandir}/man1/atlasmns-trace-agent.1.gz
%{_datadir}/doc/atlasmns-trace/examples/atlasmns-database-configuration
%{_datadir}/doc/atlasmns-trace/examples/atlasmns-tracedataimporter-configuration
/etc/cron.d/atlasmns-tracedataimporter


%changelog
* Fri Dec 08 2023 Thomas Dreibholz <thomas.dreibholz@gmail.com> - 0.4.10
- New upstream release.
* Tue Feb 14 2023 Thomas Dreibholz <thomas.dreibholz@gmail.com> - 0.4.9
- New upstream release.
* Sun Sep 11 2022 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.8
- New upstream release.
* Fri Sep 10 2021 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.7
- New upstream release.
* Wed Jul 07 2021 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.6
- New upstream release.
* Fri Nov 13 2020 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.5
- New upstream release.
* Wed Jan 29 2020 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.4
- New upstream release.
* Thu Dec 19 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.3
- New upstream release.
* Thu Nov 07 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.2
- New upstream release.
* Thu Sep 26 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.1
- New upstream release.
* Thu Aug 22 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.4.0
- New upstream release.
* Tue Aug 20 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.3.3
- New upstream release.
* Fri Aug 16 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.3.2
- New upstream release.
* Wed Aug 14 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.3.1
- New upstream release.
* Mon Aug 12 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.3.0
- New upstream release.
* Thu Aug 08 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.2.5
- New upstream release.
* Tue Aug 06 2019 Thomas Dreibholz <dreibh@simula.no> - 0.2.4
- New upstream release.
* Fri Aug 02 2019 Thomas Dreibholz <dreibh@simula.no> - 0.2.3
- New upstream release.
* Fri Aug 02 2019 Thomas Dreibholz <dreibh@simula.no> - 0.2.2
- New upstream release.
* Fri Aug 02 2019 Thomas Dreibholz <dreibh@simula.no> - 0.2.1
- New upstream release.
* Wed Jul 31 2019 Thomas Dreibholz <dreibh@simula.no> - 0.2.0
- New upstream release.
* Wed Jul 31 2019 Thomas Dreibholz <dreibh@simula.no> - 0.1.3
- New upstream release.
* Tue Jul 30 2019 Thomas Dreibholz <dreibh@simula.no> - 0.1.2
- New upstream release.
* Tue Jul 30 2019 Thomas Dreibholz <dreibh@simula.no> - 0.1.1
- New upstream release.
* Tue Jul 30 2019 Thomas Dreibholz <dreibh@simula.no> - 0.1.0
- New upstream release.
* Fri Jun 14 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
