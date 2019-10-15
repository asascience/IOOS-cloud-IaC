Name:           bacio
Version:        v2.1.0
Release:        1%{?dist}
Summary:        NCEPLIBS %{name} library

License:        GPL+
URL:            https://github.com/NOAA-EMC/NCEPLIBS-bacio
Source0:        https://github.com/NOAA-EMC/NCEPLIBS-bacio.git

#Requires:

BuildArch:       x86_64

%define bbase $BBASE
%define builtdir %{bbase}/%{name}/%{version}

%description
NOAA/NCEP library used in numerical weather prediction models.

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/nceplibs/%{name}/%{version}/
cp %{builtdir}/* %{buildroot}/usrx/nceplibs/%{name}/%{version}

# Create modulefile
mkdir -p %{buildroot}/usrx/modulefiles/%{name}
cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for %{name} %{version}"
}

setenv GROUPROOT /usrx
set lname bacio
set bname BACIO
set ver %{version}

set NCEPLIBS $::env(GROUPROOT)/nceplibs
set dlib \$NCEPLIBS/\${lname}/\${ver}

setenv \${bname}_SRC  \$dlib/sorc
setenv \${bname}_INC4 " "
setenv \${bname}_INC8 " "
setenv \${bname}_INCd " "
setenv \${bname}_LIB4 \$dlib/lib\${lname}_\${ver}_4.a 
setenv \${bname}_LIB8 \$dlib/lib\${lname}_\${ver}_8.a
setenv \${bname}_VER \$ver

EOF



%files
   %dir /usrx/nceplibs/%{name}/%{version}
   /usrx/nceplibs/%{name}/%{version}/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/nceplibs/%{name}/%{version}

%postun

   ldconfig -n /usrx/nceplibs/%{name}/%{version}

%changelog
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
