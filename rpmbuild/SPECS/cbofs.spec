Name:	 nosofs-cbofs
Version: v3.1.9.1
Release: 2%{?dist}
Summary: NCEP Chesapeake Bay Operational Forecast System

License: ROMS
URL:	 https://tidesandcurrents.noaa.gov/ofs/cbofs/cbofs.html
Source0: https://www.nco.ncep.noaa.gov/pmb/codes/nwprod/nosofs.v3.1.9.1/sorc/

#BuildRequires:	
#Requires:	

%description
The US National ocean forecast system model from NOAA.

#/save/centos/nosofs.%{version} - built at
#/save/centos/nosofs.v3.1.9.1
%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/save/nosofs.%{version}/exec
cp -Rp /save/centos/nosofs.%{version}/exec/*        %{buildroot}/save/nosofs.%{version}/exec/
cp -Rp /save/centos/nosofs.%{version}/fix/          %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/jobs/         %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/scripts/      %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/ush/          %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/VERSION      %{buildroot}/save/nosofs.%{version}/


%files

%dir /save/nosofs.%{version}
/save/nosofs.%{version}/*

%changelog
* Tue Oct 15 2019 Patrick Tripp <patrick.tripp@rpsgroup.com> 3.1.9.1-2
- Built with newer intel/mpi/2019.5.281
* Wed Oct 2 2019 Patrick Tripp <patrick.tripp@rpsgroup.com> 3.1.9.1-1
- Initial RPM package for NOSOFS CBOFS devel
