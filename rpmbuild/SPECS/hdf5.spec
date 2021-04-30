Name:           hdf5
Version:        1.10.5
Release:        4%{?dist}
Summary:        HDF5 libraries and tools

License:        NCSA HDF
URL:            https://portal.hdfgroup.org/display/support
Source0:        https://support.hdfgroup.org/ftp/HDF5/releases

#Requires:

BuildArch:       x86_64

%description
HDF5 libraries and binaries

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
mkdir -p %{buildroot}/usrx/%{name}/%{version}/share
cp -Rp /usrx/%{name}/%{version}/bin      %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib      %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include  %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share/COPYRIGHT   %{buildroot}/usrx/%{name}/%{version}/share/

# Create a modulefile
mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for HDF library"
}
module-whatis       "Sets up the HDF5 Library environment"

set ver v%{version}
prepend-path    LD_LIBRARY_PATH  "/usrx/%{name}/%{version}/lib"
append-path     PATH             "/usrx/%{name}/%{version}/bin"
setenv HDF5_LIB "-L/usrx/%{name}/%{version}/lib -lhdf5 -lhdf5_hl -lz"
setenv HDF5_INC "-I/usrx/%{name}/%{version}/include"
setenv HDF5_LIBDIR "/usrx/%{name}/%{version}/lib"
setenv HDF5_DIR    "/usrx/%{name}/%{version}"
EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/lib/*
   /usrx/%{name}/%{version}/include/*
   %{license} /usrx/%{name}/%{version}/share/COPYRIGHT
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Tue Apr 20 2021 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Fixed missing " in modulefile
* Thu Jul 16 2020 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Updated modulefile 
* Thu Dec 12 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Upgrade to 1.10.5
* Thu Dec 12 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- 2 Added env module
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial HDF5 package
