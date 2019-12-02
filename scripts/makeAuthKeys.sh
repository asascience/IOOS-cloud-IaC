#!/bin/bash

key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDauHU/ZyfaOMC579I3Rm+sXmn17TuKZgBJ6F+2+E4lj6ISL1ltKFcfM7H9oXRLL8t18cJRpcBlAXafjzRnh9kP1rf7LJOkx9gbH/w/rCt4r9Qpk8/zfHO5Mg4RyOYfeKehnQyEUyXIwk4OsuqKqmRJrx9Xa0E23Zs1YuR34HmeCA/8PaO3Bx1arO231fndkKkWMVvIleIptd8+q5rjZ6bVXTGog8TWxx5iAE5a8QtdfjHIeHanv618t9JweStm0zCTu/iy59Ploh4nT7E01iIM6lEvw5d5wLIFuCeh6Frf7L5X/+p/lDIeTwIBi76Z8hovM88WZSoTOkmd9KvPBZq9"

hostprint="ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBDJn2J0OVrWMg6NmHa/eA7V2SdmdSJs47xk493uFrKgu9zhcBZ8224dX85AAPn3Ky7D8q3KOe14PA1DnYMFISdI="

#"ip-10-0-0-14.ec2.internal,10.0.0.14"

iplist="0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15"


for ip in $iplist
do
  #mach="centos@ip-10-0-0-${ip}.ec2.internal"
  #echo "$key $mach" >> ~/.ssh/authorized_keys

  host="ip-10-0-0-${ip}.ec2.internal,10.0.0.${ip}"
  echo "$host $hostprint" >> ~/.ssh/known_hosts
done

