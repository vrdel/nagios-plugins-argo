%define dir %{_libdir}/nagios/plugins/argo

Name: nagios-plugins-argo
Summary: ARGO components related probes.
Version: 0.1.1
Release: 1%{?dist}
License: ASL 2.0
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Group: Network/Monitoring
BuildArch: noarch
Requires: python-requests, pyOpenSSL, python-argparse

%description
This package includes probes for ARGO components. 
Currently it supports the following components:
 - ARGO Web API
 - POEM

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
install --directory ${RPM_BUILD_ROOT}%{dir}
install --mode 755 src/*  ${RPM_BUILD_ROOT}%{dir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{dir}


%changelog
* Mon Sep 5 2016 Daniel Vrcic <daniel.vrcic@gmail.com>, Filip Mendusic <filip.mendjusic@gmail.com> - 0.1.1-1%{?dist}
* POEM probe: certificate and REST API checks
* Thu Aug 25 2016 Themis Zamani <themis@grnet.gr> - 0.1.0-1%{?dist}
- ARGO WEB API probe: Check if api returns results.
