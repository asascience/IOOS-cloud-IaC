Name:           zlib
Version:        1.2.11
Release:        1%{?dist}
Summary:        The compression and decompression library

License:        zlib and Boost
URL:            http://www.zlib.net/

#Requires:

BuildArch:       x86_64

%description
Zlib is a general-purpose, patent-free, lossless data compression 
library which is used by many different programs.

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include   %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share   %{buildroot}/usrx/%{name}/%{version}/

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for Z library
}
module-whatis       "Sets up the Z Library environment"

set ver v%{version}
setenv Z_LIB "-L/usrx/%{name}/%{version}/lib -lz"
EOF

%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/lib/*
   /usrx/%{name}/%{version}/include/*
   /usrx/%{name}/%{version}/share/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Fri Sep 20 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
