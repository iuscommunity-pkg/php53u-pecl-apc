%{!?__pecl:     %{expand: %%global __pecl     %{_bindir}/pecl}}
%{!?pecl_phpdir: %{expand: %%global pecl_phpdir  %(%{__pecl} config-get php_dir  2> /dev/null || echo undefined)}}
%{?!pecl_xmldir: %{expand: %%global pecl_xmldir %{pecl_phpdir}/.pkgxml}}

%define php_extdir %(php-config --extension-dir 2>/dev/null || echo %{_libdir}/php4)                     
%global php_zendabiver %((echo 0; php -i 2>/dev/null | sed -n 's/^PHP Extension => //p') | tail -1)
%global php_version %((echo 0; php-config --version 2>/dev/null) | tail -1)
%define pecl_name APC
%{?!_without_php_ver_tag: %define php_ver_tag .php%{php_major_version}}

%define real_name php-pecl-apc
%define base_ver 3.0
%define php_base php53u
#%%define patchver p1

Summary:        APC caches and optimizes PHP intermediate code
Name:           %{php_base}-pecl-apc
Version:        3.1.9%{?patchver}
Release:        4.ius%{?dist}
License:        PHP
Group:          Development/Languages
Vendor:         IUS Community Project 
URL:            http://pecl.php.net/package/APC
Source:         http://pecl.php.net/get/APC-%{version}.tgz
Source1:	apc.ini

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
Conflicts:      %{php_base}-mmcache %{php_base}-eaccelerator 
Conflicts:      %{php_base}-zend-optimizer %{php_base}zend-optimizer
Provides:       %{real_name} = %{version}
Conflicts:      %{real_name} < %{base_ver}
BuildRequires:  %{php_base}-devel %{php_base}-cli httpd-devel %{php_base}-pear 
BuildRequires:  pcre-devel 
# php53u now builds pcre from php source
Requires:       %{php_base} >= 5.3.5-1

%if %{?php_zend_api}0
# Require clean ABI/API versions if available (Fedora)
Requires:       %{php_base}(zend-abi) = %{php_zend_api}
Requires:       %{php_base}(api) = %{php_core_api}
Requires:       %{php_base}-pear
%else
Requires:       %{php_base}-zend-abi = %{php_zendabiver}
%endif
Provides:      php-pecl(%{pecl_name}) = %{version}

Requires(post): %{__pecl}
Requires(postun): %{__pecl}

# FIX ME: This should be removed before/after RHEL 5.6 is out
# See: https://bugs.launchpad.net/ius/+bug/691755


%description
APC is a free, open, and robust framework for caching and optimizing PHP
intermediate code.

%prep
%setup -q -n %{pecl_name}-%{version}

%build
%{_bindir}/phpize
%configure --enable-apc-memprotect --with-apxs=%{_sbindir}/apxs --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%{__make} install INSTALL_ROOT=%{buildroot}

# Install the package XML file
%{__mkdir_p} %{buildroot}%{pecl_xmldir}
%{__install} -m 644 ../package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Drop in the bit of configuration
%{__mkdir_p} %{buildroot}%{_sysconfdir}/php.d
%{__install} -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/php.d/apc.ini


# Fix the charset of NOTICE
iconv -f iso-8859-1 -t utf8 NOTICE >NOTICE.utf8
mv NOTICE.utf8 NOTICE

%post
%{__pecl} install --nodeps --soft --force --register-only --nobuild %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ]  ; then
%{__pecl} uninstall --nodeps --ignore-errors --register-only %{pecl_name} >/dev/null || :
fi

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc TECHNOTES.txt CHANGELOG LICENSE NOTICE TODO INSTALL apc.php
%config(noreplace) %{_sysconfdir}/php.d/apc.ini
%{php_extdir}/apc.so
%{pecl_xmldir}/%{pecl_name}.xml
%{_includedir}/php/ext/apc/apc_serializer.h

%changelog
* Fri Aug 19 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-4.ius
- Rebuilding

* Fri Aug 12 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-3.ius
- Building with EL6 support

* Wed May 25 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-2.ius
- Majority of apc.ini is commented out to allow APC's defaults
  to take control
- apc.ini is now installed from %%{SOURCE1} rather standardout

* Mon May 16 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.9-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.9

* Wed May 04 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.8-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.8

* Tue Apr 26 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.7-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.7

* Tue Feb 01 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.6-4.ius
- Removed Obsoletes: php53*

* Tue Jan 11 2011 Jeffrey Ness <jeffrey.ness@rackspace.com> - 0:3.1.6-3.ius
- Added Requires: %%{php_base} >= 5.3.5-1 as php53u now builds
  pcre from PHP Source
- Removed if {rhel} block

* Fri Dec 16 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.6-2.ius
- Changing name to php53u-pecl-apc per LP#691755
- BuildRequires: php-cli 
- Rebuild against php-5.3.4
- Obsoletes: php53-pecl-apc < 3.1.6-2

* Mon Dec 06 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.6-1.ius
- Latest sources from upstream.  Full changelog available at:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.6

* Mon Aug 30 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.4-1.ius
- Latest sources from upstream.  Full changelog available here:
  http://pecl.php.net/package-changelog.php?package=APC&release=3.1.4
- Option '--enable-apc-mmap' became '--enable-apc-memprotect'.
- Add the 'M' suffix on memory values in the .ini settings per new
  config rules.

* Mon Jul 27 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.3p1-6.ius
- Rebuild for php 5.3.3

* Mon Jun 28 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.3p1-5.ius
- BuildRequires: pcre-devel

* Tue Jun 22 2010 BJ Dierkes <wdierkes@rackspace.com> - 0:3.1.3p1-4.ius
- BuildRequires: php53-pear (not php-pear18)
- Requires: php53-pear
- Change Vendor: IUS Community Project

* Fri Oct 16 2009 BJ Dierkes <wdierkes@rackspace.com> - 0:3.0.19-3.ius
- Rebuilding for IUS

* Mon Sep 28 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:3.0.19-2.1.rs
- Rebuilding against new php.

* Mon Sep 14 2009 BJ Dierkes <wdierkes@rackspace.com> - 1:3.0.19-2.rs
- Adding Epoch: 1 due to conflicts with EPEL packages and stock php.

* Fri Jan 23 2009 BJ Dierkes <wdierkes@rackspace.com> - 3.0.19-1.2.rs
- Adding php_ver_tag to release for different major versions of PHP.
- Conflicts with php-zend-optimizer

* Tue Jan 06 2009 BJ Dierkes <wdierkes@rackspace.com> - 3.0.19-1.1.rs
- Rebuild

* Wed Jun 25 2008 Tim Jackson <rpm@timj.co.uk> - 3.0.19-1
- Update to 3.0.19
- Fix PHP Zend API/ABI dependencies to work on EL-4/5
- Fix "License" tag
- Fix encoding of "NOTICE" file
- Add registration via PECL

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.0.14-3
- Autorebuild for GCC 4.3

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 3.0.14-2
- Rebuild for selinux ppc32 issue.

* Thu Jun 28 2007 Chris Chabot <chabotc@xs4all.nl> - 3.0.14-1
- Updated to 3.0.14
- Included new php api snipplets

* Fri Sep 15 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.12-5
- Updated to new upstream version

* Mon Sep 11 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-5
- FC6 rebuild 

* Sun Aug 13 2006 Chris Chabot <chabotc@xs4all.nl> - 3.0.10-4
- FC6T2 rebuild

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-3
- Renamed to php-pecl-apc and added provides php-apc
- Removed php version string from the package version

* Mon Jun 19 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-2
- Trimmed down BuildRequires
- Added Provices php-pecl(apc)

* Sun Jun 18 2006 - Chris Chabot <chabotc@xs4all.nl> - 3.0.10-1
- Initial package, templated on already existing php-json 
  and php-eaccelerator packages
