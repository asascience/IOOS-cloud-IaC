Name:		gcc
Version:	6.5.0
Release:	1%{?dist}
Summary:	Various compilers (C, C++, Objective-C, Fortran ...)

License:	GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD
URL:		http://gcc.gnu.org

#BuildRequires:	
#Requires:	

%description
The gcc package contains the GNU Compiler Collection version %{version}


%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/* %{buildroot}/usrx/%{name}/%{version}/

mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
##
## GNU Compiler Collection
##

proc ModulesHelp { } {
        global dotversion
        puts stderr " Intel(R) MPI Library"
}

module-whatis       "Sets up the GCC compiler environment"

set                 topdir                 /usrx/gcc/%{version}

prepend-path        PATH                   \$topdir/bin
prepend-path        LD_LIBRARY_PATH        \$topdir/lib
prepend-path        LD_LIBRARY_PATH        \$topdir/lib64
prepend-path        MANPATH                \$topdir/share/man
EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib64
   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib
   ldconfig -n /usrx/%{name}/%{version}/lib64


%changelog
* Wed Sep 25 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial gcc 6.5.0 package

