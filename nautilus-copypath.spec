Name:           nautilus-copypath
Version:        0.0.1
Release:        1%{?dist}
License:        GPLv3+
Summary:        A small Nautilus extension for quickly copying file/Samba paths.
Url:            https://github.com/ronen25/%{srcname}
Source0:        %{name}-%{version}.tar.gz

Requires:       nautilus-python
Requires:       python3-gobject

BuildArch:  noarch

%global srcname %{name}.py

%description
A small Nautilus extension for quickly copying file/Samba paths.

#-- PREP, BUILD & INSTALL -----------------------------------------------------#
%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/%{_datadir}/nautilus-python/extensions
install -m 755 %{srcname} %{buildroot}/%{_datadir}/nautilus-python/extensions/%{srcname}

#-- FILES ---------------------------------------------------------------------#
%files
%doc README.md
%license LICENSE
%{_datadir}/nautilus-python/extensions/%{srcname}

#-- CHANGELOG -----------------------------------------------------------------#
%changelog
* Tue Sep 19 2023 Fynn Freyer <fynn.freyer@googlemail.com> 0.0.1
- setup package build with tito
