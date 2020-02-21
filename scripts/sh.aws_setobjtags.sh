#!/usr/bin/python3

buckets='
cf-templates-y20cx16e76yc-us-east-1
cf-templates-y20cx16e76yc-us-east-2
ioos-cloud
ioos-cloud-sandbox
ioos-code-sprint-2019
ioos-comt
ioos-eds
ioos-eds-config
ioos-eds-dev
ioos-status
ott-radial
react-page-container-dev-20190717152509-deployment
react-page-container-dev-20191003104014-deployment
react-page-container-test-20191001125340-deployment
rps-glos
rps-glos-config
rps-glos-data
'
declare -a projects

buckets='ioos-cloud-sandbox'

projects=(
RPS
RPS
IOOS-cloud
IOOS-cloud-sandbox
IOOS-cloud
IOOS-COMT
IOOS-EDS
IOOS-EDS
IOOS-EDS
IOOS-EDS
OTT-RADIAL
RPS
RPS
RPS
RPS-GLOS
RPS-GLOS
RPS-GLOS
)

index=0

for bucket in $buckets
do

  #aws s3api list-objects --bucket <value>
  aws s3api list-objects --bucket $bucket
  # aws s3api put-object-tagging
  project=${projects[$index]}
  echo "bucket: $bucket  Project: $project"
  ((index += 1))
done
