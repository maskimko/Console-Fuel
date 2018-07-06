Name:	python3-console-fuel
Version: 0.95
BuildArch: noarch
Release:	1%{?dist}
Summary: Simple python 3 client to get fuel prices from minfin.com.ua

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
* Fri Jul 07 2018 Maksym Shkolnyi <maskimko@ukr.net> - 0.95
- Yellow button update on minfin site
* Tue Mar 03 2018 Maksym Shkolnyi <maskimko@ukr.net> - 0.9
- Update of minfin.com.ua table parsing
* Wed Jan 31 2018 Maksym Shkolnyi <maskimko@ukr.net> - 0.8
- Beautification of code
- Fixed columns order
* Mon Jan 29 2018 Maksym Shkolnyi <maskimko@ukr.net> - 0.7
- Fixed columns order
* Mon Dec 18 2017 Maksym Shkolnyi <maskimko@ukr.net> - 0.6
- Changes in the source interface
* Tue Nov 28 2017 Maksym Shkolnyi <maskimko@ukr.net> - 0.4
- Switched to the data from minfin.com.ua
- Added petrol and LPG prices
- Fixed missing fuel table shifting
- Fixed order of the table heading
- Updated shebang
* Fri Nov 24 2017 Maksym Shkolnyi <maskimko@ukr.net> - 0.1
- First packaging attempt

