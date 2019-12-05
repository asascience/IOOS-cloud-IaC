Name:           produtil
Version:        1.0.18
Release:        2%{?dist}
Summary:        Date and other utilities used in NCO production suite

License:        GPL+
URL:            https://github.com/NOAA-EMC/fv3gfs/tree/master/external/prod_util-1.0.18
Source0:        https://github.com/NOAA-EMC/fv3gfs/tree/master/external/prod_util-1.0.18 

#Requires:       NCEPLIBS w3nco to build

BuildArch:      x86_64

#%define builtdir /home/ec2-user/nosofs-prereqs/builds/%{name}-%{version}
%define builtdir /usrx/%{name}/%{version}

%description
ndate - get now date in format YYYYMMDDHH, optionally +/- N hours
mdate - get now date in format YYYYMMDDHHMM, optionally +/- M minutes
nhour - get number of hours between dates in YYYYMMDDHH format
./ush directory has other scripts used by various scripts

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/usrx/%{name}/%{version}/
cp -Rp %{builtdir}/exec %{buildroot}/usrx/%{name}/%{version}/
cp -Rp %{builtdir}/para_dbn %{buildroot}/usrx/%{name}/%{version}/
cp -Rp %{builtdir}/fakedbn %{buildroot}/usrx/%{name}/%{version}/
cp -Rp %{builtdir}/ush %{buildroot}/usrx/%{name}/%{version}/


mkdir -p %{buildroot}/usrx/modulefiles/%{name}

cat > %{buildroot}/usrx/modulefiles/%{name}/%{version} <<-EOF
#%Module1.0#####################################################################
## NCEP prod utils
proc ModulesHelp { } {
        puts stderr "Set environment veriables for %{name} %{version}"
}

set topdir /usrx/%{name}/%{version}

append-path PATH \$topdir/ush
append-path PATH \$topdir/exec

setenv NDATE  \$topdir/exec/ndate
setenv MDATE  \$topdir/exec/mdate
setenv NHOUR  \$topdir/exec/nhour

EOF


%files
   %dir /usrx/%{name}/%{version}
   /usrx/%{name}/%{version}/*
   /usrx/modulefiles/%{name}/%{version}

%changelog
* Thu Dec 5 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Removed forced kill of process group in ush err_exit
* Wed Sep 18 2019 Patrick Tripp <patrick.tripp@rpsgroup.com>
- Initial %{name} package
