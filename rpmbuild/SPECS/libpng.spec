Name:           libpng
Version:        1.5.30
Release:        2%{?dist}
Summary:        A library of functions for manipulating PNG image format files 

License:        zlib
URL:            http://www.libpng.org

BuildArch:       x86_64

%description
The libpng package contains a library of functions for creating and
manipulating PNG (Portable Network Graphics) image format files.  PNG
is a bit-mapped graphics format similar to the GIF format.  PNG was
created to replace the GIF format, since GIF uses a patented data
compression algorithm.


%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/modulefiles/%{name}/
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/bin     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/include   %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/lib     %{buildroot}/usrx/%{name}/%{version}/
cp -Rp /usrx/%{name}/%{version}/share   %{buildroot}/usrx/%{name}/%{version}/

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
proc ModulesHelp { } {
        puts stderr "Set environment veriables for PNG library
}

module-whatis       "Sets up the PNG Library environment"

set ver v%{version}

setenv       PNG_LIB          "-L/usrx/%{name}/%{version}/lib -lpng"
setenv       PNG_INC          "-I/usrx/%{name}/%{version}/include"
append-path  LD_LIBRARY_PATH  /usrx/%{name}/%{version}/lib
EOF

%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/bin/*
   /usrx/%{name}/%{version}/lib/*
   /usrx/%{name}/%{version}/include/*
   /usrx/%{name}/%{version}/share/*
   /usrx/modulefiles/%{name}/%{version}

%post

   ldconfig -n /usrx/%{name}/%{version}/lib

%postun

   ldconfig -n /usrx/%{name}/%{version}/lib

%changelog
* Thu Jul 16 2020 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Updated modulefile
* Fri Sep 20 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
