Name:           netcdf
Version:        4.5
Release:        3%{?dist}
Summary:        NetCDF precompiled libraries and tools

License:        NetCDF
URL:            https://www.unidata.ucar.edu/downloads/netcdf/index.jsp
Source0:        https://www.unidata.ucar.edu/downloads/netcdf/index.jsp

#Requires:

BuildArch:       x86_64

%description
Includes C, C++, and Fortran libraries built with GCC version 6.50 and
Gnu Fortran gfortran version 6.5.0
This was build using hdf5 serial v1.10.5


%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share %{buildroot}/usrx/%{name}/%{version}/

gzip -fq %{buildroot}/usrx/%{name}/%{version}/share/man/man1/*
gzip -fq %{buildroot}/usrx/%{name}/%{version}/share/man/man3/*

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for netcdf %{version} parallel enabled" 
}

setenv       NETCDF /usrx/%{name}/%{version}
append-path  LD_LIBRARY_PATH /usrx/%{name}/%{version}/lib
append-path  PATH  /usrx/%{name}/%{version}/bin

EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/include/*
   /usrx/%{name}/%{version}/lib/*
   %{license} /usrx/%{name}/%{version}/share/COPYRIGHT
   /usrx/%{name}/%{version}/share/man/man1/*
   /usrx/%{name}/%{version}/share/man/man3/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Thu Dec 12 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- rebuilt using HDF5 serial v1.10.5
* Thu Dec 12 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- rebuilt using serial HDF5
* Thu Dec 5 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Upgrade to version 4.5 
- Removed '64' from 'lib64'
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial netcdf package
