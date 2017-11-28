Name:	python3-console-fuel
Version: 0.2
BuildArch: noarch
Release:	1%{?dist}
Summary: Simple python 3 client to get diesel prices from minfin.com.ua

Group:	Applications/Scripts
License: GPL v3
URL:	http://git.kyi.msk	
Source0: fuelprice.py

Requires: python3 > 3, python3-urllib3, system-python-libs > 3, python3-terminaltables, python3-termcolor, python3-certifi

%description
This client works with python 3 interpreter. It fetches fuel prices html page data from minfin.com.ua and represents it as a table

%prep
#%setup -q


%build


%install
install -d %{buildroot}%{_libdir}/python3.6/site-packages/console-fuel
install -m 0775 %{SOURCE0} %{buildroot}%{_libdir}/python3.6/site-packages/console-fuel/fuelprice.py
install -d  %{buildroot}%{_bindir}
ln -s %{_libdir}/python3.6/site-packages/console-fuel/fuelprice.py %{buildroot}%{_bindir}/fuel-price

%files
#%doc
%defattr(-,root, root)
%{_libdir}/python3.6/site-packages/console-fuel
%{_bindir}/fuel-price


%changelog
* Tue Nov 28 2017 Maksym Shkolnyi <maskimko@ukr.net> - 0.2
- Switched to the data from minfin.com.ua
* Fri Nov 24 2017 Maksym Shkolnyi <maskimko@ukr.net> - 0.1
- First packaging attempt

