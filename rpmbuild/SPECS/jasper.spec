Name:           jasper
Version:        1.900.1
Release:        1%{?dist}
Summary:        Implementation of the JPEG-2000 standard, Part 1

License:        JasPer
URL:            https://www.ece.uvic.ca/~frodo/jasper/

#Requires:

BuildArch:       x86_64

%description
This package contains an implementation of the image compression
standard JPEG-2000, Part 1. It consists of tools for conversion to and
from the JP2 and JPC formats, and includes headers and libraries.

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include   %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/man   %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /home/ec2-user/nosofs-prereqs/builds/jasper-1.900.1/LICENSE %{buildroot}/usrx/%{name}/%{version}/

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for Jasper library
}
module-whatis       "Sets up the Jasper Library environment"

set ver v%{version}
setenv JASPER_LIB "-L/usrx/%{name}/%{version}/lib -ljasper"
setenv JASPER_INC "-I/usrx/%{name}/%{version}/include"

EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/lib/*
   /usrx/%{name}/%{version}/man/*
   /usrx/%{name}/%{version}/include/*
   /usrx/modulefiles/%{name}/%{version}
   %license /usrx/%{name}/%{version}/LICENSE

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Fri Sep 20 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
