Name:           netcdf
Version:        4.2
Release:        1%{?dist}
Summary:        NetCDF precompiled libraries and tools

License:        NetCDF
URL:            ftp://ftp.unidata.ucar.edu/pub/netcdf/old
Source0:        ftp://ftp.unidata.ucar.edu/pub/netcdf/old/netcdf-4.2.tar.gz
Source1:        ftp://ftp.unidata.ucar.edu/pub/netcdf/old/netcdf-fortran-4.2.tar.gz
Source2:        ftp://ftp.unidata.ucar.edu/pub/netcdf/netcdf-cxx-4.2.tar.gz

#Requires:

BuildArch:       x86_64

%description
Includes C, C++, and Fortran libraries built with GCC version 7.2.1 and 
Gnu Fortran gfortran version 6.4.1


%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib64 %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share %{buildroot}/usrx/%{name}/%{version}/

gzip -fq %{buildroot}/usrx/%{name}/%{version}/share/man/man1/*
gzip -fq %{buildroot}/usrx/%{name}/%{version}/share/man/man3/*

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for netcdf %{version}"
}

setenv       NETCDF /usrx/%{name}/%{version}
append-path  LD_LIBRARY_PATH /usrx/%{name}/%{version}/lib64
append-path  PATH  /usrx/%{name}/%{version}/bin

EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/include/*
   /usrx/%{name}/%{version}/lib64/*
   %{license} /usrx/%{name}/%{version}/share/COPYRIGHT
   /usrx/%{name}/%{version}/share/info/*
   /usrx/%{name}/%{version}/share/man/man1/*
   /usrx/%{name}/%{version}/share/man/man3/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib64

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib64

%changelog
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial netcdf package
