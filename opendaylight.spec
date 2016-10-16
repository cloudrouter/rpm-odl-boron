%global project_name opendaylight
%global release_name boron
%global release_version 0.5.0
%global source_url https://nexus.opendaylight.org/content/groups/public/org/opendaylight/integration/distribution-karaf/0.5.0-Boron/distribution-karaf-0.5.0-Boron.tar.gz

%define __jar_repack 0

Name: %{project_name}-%{release_name}
Summary: OpenDaylight SDN Controller
Version: %{release_version}
Release: 1%{?dist}
Source0: %{source_url}
Source1: %{project_name}.service
Patch0: 0001-opendaylight-remove-credentials.patch
Group: Applications/Communications
License: EPL-1.0
URL: http://www.opendaylight.org
BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-buildroot

%{?rhel:Requires: java-1.8.0-openjdk-devel}
%{?fedora:Requires: java-devel >= 1.8.0}
Requires(pre): shadow-utils, glibc-common
Requires(postun): shadow-utils

BuildRequires: systemd

Conflicts: opendaylight-helium
Conflicts: opendaylight-lithium
Conflicts: opendaylight-beryllium

# this is used to identify if we need to remove the odl user/group when
# removing
Provides: %{project_name}

%pre
%global odl_user odl
%global odl_home /opt/%{project_name}

# Create odl user/group
getent passwd %{odl_user} > /dev/null \
    || useradd --system --home-dir %{odl_home} %{odl_user}
getent group %{odl_user} > /dev/null \
    || groupadd --system %{odl_user}

# disable debug packages and the stripping of the binaries
%global _enable_debug_package 0
%global debug_package %{nil}
%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

%description
OpenDaylight is an open platform for network programmability to enable SDN and create a solid foundation for NFV for networks at any size and scale.

%prep
ROOT_DIR=$(dirname $(tar -tf %{SOURCE0} | head -n 1))
%autosetup -N -c -n %{name}
mv ${ROOT_DIR}/* .
rm -rf ${ROOT_DIR}
%autopatch -p0

%build

%install
install -d %{buildroot}%{odl_home}
cp -R %{_builddir}/%{name} %{buildroot}%{odl_home}
install -D %{SOURCE1} %{buildroot}%{_unitdir}/%{project_name}.service

%clean
rm -rf %
 
%post
%systemd_post %{project_name}.service

%postun
%systemd_postun_with_restart %{project_name}.service

# remove installed files
rm -rf %{odl_home}/%{name}

# remove odl user/group if no other opendaylight package is installed
rpmquery --query --whatprovides opendaylight > /dev/null \
    || { userdel %{odl_user} && groupdel %{odl_user}; }

%files
# ODL uses systemd to run as user:group odl:odl
%attr(0775,odl,odl) %{odl_home}/%{name}
%attr(0644,-,-) %{_unitdir}/%{project_name}.service

%changelog
* Sun Oct 16 2016 John Siegrist <john@complects.com> - 0.5.0-1
- Initial version forked from the CloudRouter ODL-Beryllium spec