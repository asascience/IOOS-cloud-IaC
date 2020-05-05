Name:           esmf
Version:        8.0.0
Release:        1%{?dist}
Summary:        ESMF libraries and applications

License:        ESMF
URL:            https://www.earthsystemcog.org/projects/esmf/
Source0:        https://sourceforge.net/p/esmf/esmf/ci/ESMF_8_0_0/tree

BuildArch:      x86_64

%description
    A high-performance, flexible software infrastructure for building and 
coupling weather, climate, and related Earth science applications.

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin      %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include  %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib      %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/mod      %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share    %{buildroot}/usrx/%{name}/%{version}/

# Create a modulefile
mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment variables for ESMF library"
}
module-whatis       "Sets up the ESMF library environment"

set ver v%{version}
prepend-path  LD_LIBRARY_PATH  "/usrx/%{name}/%{version}/lib/libO/Linux.gfortran.64.intelmpi.default"
prepend-path  PATH             "/usrx/%{name}/%{version}/bin/binO/Linux.gfortran.64.intelmpi.default"
setenv        ESMFMKFILE       "/usrx/%{name}/%{version}/lib/libO/Linux.gfortran.64.intelmpi.default/esmf.mk
EOF

%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/include/*
   /usrx/%{name}/%{version}/lib/*
   /usrx/%{name}/%{version}/mod/*
   %{license} /usrx/%{name}/%{version}/share/LICENSE
   /usrx/modulefiles/%{name}/%{version}

%post
   ldconfig -n /usrx/%{name}/%{version}/lib/libO/Linux.gfortran.64.intelmpi.default

%postun
   ldconfig -n /usrx/%{name}/%{version}/lib/libO/Linux.gfortran.64.intelmpi.default

%changelog
* Tue May 5 2020 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial ESMF build
