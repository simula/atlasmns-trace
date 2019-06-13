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

%description scheduler
 Atlas/MNS Trace Scheduler is the scheduler for the Atlas/MNS Trace experiments.
 See https://www.nntb.no for details on NorNet!

%files scheduler
%{_bindir}/atlasmns-trace-scheduler
%{_mandir}/man1/atlasmns-trace-scheduler.1.gz


%package agent
Summary: Atlas/MNS Trace Agent
Group: Applications/Internet
BuildArch: noarch
Requires: hipercontracer (>= 1.4.0~)
Requires: nornet-trace-trigger

%description agent
 Atlas/MNS Trace Agent is the agent for the Atlas/MNS Trace experiments.
 See https://www.nntb.no for details on NorNet!

%files agent
%{_bindir}/atlasmns-trace-agent
%{_mandir}/man1/atlasmns-trace-agent.1.gz



%changelog
* Thu Jun 14 2019 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
