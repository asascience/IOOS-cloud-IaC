Name:           hdf5-impi
Version:        1.8.21
Release:        1%{?dist}
Summary:        HDF5 libraries and tools

License:        NCSA HDF
URL:            https://portal.hdfgroup.org/display/support
Source0:        https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.21/src

#Requires:

BuildArch:       x86_64

%description
HDF5 libraries and binaries built with Intel MPI libraries

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
setenv HDF5_LIB "-L/usrx/%{name}/%{version}/lib -lhdf5 -lhdf5_hl"
setenv HDF5_INC "-I/usrx/%{name}/%{version}/include"

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
* Thu Dec 5 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- HDF5 with parallel support
