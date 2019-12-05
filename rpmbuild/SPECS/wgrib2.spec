Name:           wgrib2
Version:        2.0.8
Release:        2%{?dist}
Summary:        Date and other utilities used in NCO production suite

License:        HDF5 and NCSA HDF5 and JasPer and libpng and UCAR and zlib and BSD
URL:            https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/
Source0:        ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz

BuildArch:       x86_64

%define builtdir /usrx/wgrib2/2.0.8

%description
wgrib2 utility from NCEP
process and work with grib2 files
built with Gnu CC and gfortran, netcdf4

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/bin
mkdir -p %{buildroot}/usrx/%{name}/%{version}/docs
mkdir -p %{buildroot}/usrx/%{name}/%{version}/share

cp -p %{builtdir}/bin/wgrib2 %{buildroot}/usrx/%{name}/%{version}/bin
cp -p %{builtdir}/share/LICENSE* %{buildroot}/usrx/%{name}/%{version}/share
cp -p %{builtdir}/docs/formats.doc %{buildroot}/usrx/%{name}/%{version}/docs/
cp -p %{builtdir}/docs/intro*.doc %{buildroot}/usrx/%{name}/%{version}/docs/

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
## NCEP prod utils
proc ModulesHelp { } {
        puts stderr "Set environment veriables for %{name} %{version}"
}

set topdir /usrx/%{name}/%{version}

setenv WGRIB2 \$topdir/bin/wgrib2
setenv WGRIB  \$topdir/bin/wgrib2
append-path   PATH  \$topdir/bin

EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/*
   /usrx/modulefiles/%{name}/%{version}
   %license /usrx/%{name}/%{version}/share/LICENSE-g2clib
   %license /usrx/%{name}/%{version}/share/LICENSE-hdf
   %license /usrx/%{name}/%{version}/share/LICENSE-jasper
   %license /usrx/%{name}/%{version}/share/LICENSE-libpng
   %license /usrx/%{name}/%{version}/share/LICENSE-netcdf
   %license /usrx/%{name}/%{version}/share/LICENSE-wgrib2
   %license /usrx/%{name}/%{version}/share/LICENSE-zlib
   %doc /usrx/%{name}/%{version}/docs/*

%changelog
* Thu Dec 5 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- put binary in bin folder
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
