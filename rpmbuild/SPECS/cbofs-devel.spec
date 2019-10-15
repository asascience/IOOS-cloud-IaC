Name:	 nosofs-cbofs-fcst-devel
Version: v3.1.9.1
Release: 2%{?dist}
Summary: NCEP Chesapeake Bay Operational Forecast System

License: ROMS and Public Domain 
URL:	 https://tidesandcurrents.noaa.gov/ofs/cbofs/cbofs.html
#Source0: https://www.nco.ncep.noaa.gov/pmb/codes/nwprod/nosofs.v3.1.9.1/sorc/

# BuildRequires: hdf5 environment-modules netcdf mpi
#Requires: hdf5 jasper libpng environment-modules netcdf zlib bacio bufr g2 nemsio sigio w3emc w3nco

%description
The US National ocean forecast system model from NOAA. This contains all 
sources and build instructions. It also includes all scripts and files 
required to run the model forecast and nowcast. 
See sorc/ROMS_COMPILE.sh to build.

%install
module load mpi/intel/2019.5.281
rm -Rf %{buildroot}
mkdir -p %{buildroot}/save/nosofs.%{version}/sorc/
cp -Rp /save/centos/nosofs.%{version}/exec/         %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/fix/          %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/jobs/         %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/modulefiles/  %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/scripts/      %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/sorc/ROMS.fd/ %{buildroot}/save/nosofs.%{version}/sorc/
cp -Rp /save/centos/nosofs.%{version}/ush/          %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/VERSION       %{buildroot}/save/nosofs.%{version}/
cp -Rp /save/centos/nosofs.%{version}/sorc/ROMS_COMPILE.sh     %{buildroot}/save/nosofs.%{version}/sorc/


%files

%dir /save/nosofs.%{version}
/save/nosofs.%{version}/*

%changelog
* Tue Oct 15 2019 Patrick Tripp <patrick.tripp@rpsgroup.com> 3.1.9.1-2
- Built with newer intel/mpi/2019.5.281
* Wed Oct 2 2019 Patrick Tripp <patrick.tripp@rpsgroup.com> 3.1.9.1-1
- Initial RPM package for NOSOFS CBOFS devel
