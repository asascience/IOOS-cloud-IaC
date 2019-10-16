#!/bin/sh

# Install the cbofs model forecast binary and scripts

mkdir -p /tmp/cbofs
cd /tmp/cbofs
wget https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/nosofs-cbofs-v3.1.9.1-2.el7.x86_64.rpm
yum -y install nosofs-cbofs-v3.1.9.1-2.el7.x86_64.rpm
cd ~
rm -Rf /tmp/cbofs
mkdir -p /noscrub/com/nos
cd /noscrub/com/nos
curl https://ioos-cloud-sandbox.s3.amazonaws.com/public/cbofs/ICs.cbofs.2019100100.tgz | tar -xvz

# Fix permissions so non-root user can modify
chgrp -R wheel /noscrub
chmod -R g+w /noscrub
chgrp -R wheel /save
chmod -R g+w /save
mkdir -p /ptmp
chgrp wheel /ptmp
chmod 775 /ptmp
