Name:           w3emc
Version:        v2.2.0
Release:        1%{?dist}
Summary:        NCEPLIBS %{name} library

License:        GPL+
URL:            https://github.com/NOAA-EMC/NCEPLIBS-w3emc
Source0:        https://github.com/NOAA-EMC/NCEPLIBS-w3emc.git

#Requires:

BuildArch:       x86_64

%define bbase $BBASE
%define builtdir %{bbase}/%{name}/%{version}

%description
NOAA/NCEP library used in numerical weather prediction models.

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/nceplibs/%{name}/%{version}/
cp -Rp %{builtdir}/* %{buildroot}/usrx/nceplibs/%{name}/%{version}
# find %{buildroot}/usrx/nceplibs/%{name}/%{version} -type d -exec chmod 755 {} \;

# Create modulefile
mkdir -p %{buildroot}/usrx/modulefiles/%{name}
cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for %{name} %{version}"
}

setenv GROUPROOT /usrx
set lname w3emc
set bname W3EMC
set ver %{version}

set NCEPLIBS $::env(GROUPROOT)/nceplibs
set dlib \$NCEPLIBS/\${lname}/\${ver}

setenv \${bname}_SRC     \$dlib/sorc
setenv \${bname}_LIB4    \$dlib/lib\${lname}_\${ver}_4.a
setenv \${bname}_LIB8    \$dlib/lib\${lname}_\${ver}_8.a
setenv \${bname}_LIBd    \$dlib/lib\${lname}_\${ver}_d.a

setenv \${bname}_INC4 \${dlib}/include/\${lname}_\${ver}_4
setenv \${bname}_INC8 \${dlib}/include/\${lname}_\${ver}_8
setenv \${bname}_INCd \${dlib}/include/\${lname}_\${ver}_d

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
