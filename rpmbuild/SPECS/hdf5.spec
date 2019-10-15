Name:           hdf5
Version:        1.8.21
Release:        1%{?dist}
Summary:        HDF5 libraries and tools

License:        NCSA HDF
URL:            https://portal.hdfgroup.org/display/support
Source0:        https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.8/hdf5-1.8.21/src

#Requires:

BuildArch:       x86_64

%description
HDF5 libraries and binaries

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
mkdir -p %{buildroot}/usrx/%{name}/%{version}/share
cp -Rp /usrx/%{name}/%{version}/lib     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share/COPYRIGHT   %{buildroot}/usrx/%{name}/%{version}/share/


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/lib/*
   %{license} /usrx/%{name}/%{version}/share/COPYRIGHT

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial HDF5 package
