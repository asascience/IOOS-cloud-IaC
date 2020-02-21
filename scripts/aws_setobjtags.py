#!/usr/bin/python3

import re

import boto3

#def setobjtag (bucket: str, project: str):



def main():

    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    donetags = {         'cf-templates-y20cx16e76yc-us-east-1':'RPS', \
        'cf-templates-y20cx16e76yc-us-east-2':'RPS', \
        'ioos-cloud':'IOOS-cloud', \
        'ioos-cloud-sandbox':'IOOS-cloud-sandbox', \
        'ioos-code-sprint-2019':'IOOS-cloud', \
        }


# Error        'ioos-comt':'IOOS-COMT', \

    buckettags = { \
        'ioos-eds':'IOOS-EDS', \
        'ioos-eds-config':'IOOS-EDS', \
        'ioos-eds-dev':'IOOS-EDS', \
        'ioos-status':'IOOS-EDS', \
        'ott-radial':'OTT-RADIAL', \
        'react-page-container-dev-20190717152509-deployment':'RPS', \
        'react-page-container-dev-20191003104014-deployment':'RPS', \
        'react-page-container-test-20191001125340-deployment':'RPS', \
        'rps-glos':'RPS-GLOS', \
        'rps-glos-config':'RPS-GLOS', \
        'rps-glos-data':'RPS-GLOS' }

# Error:
# botocore.exceptions.ClientError: An error occurred (InternalError) when calling the PutObjectTagging operation (reached max retries: 4): We encountered an internal error. Please try again.

# ioos-comt/backup/Home/projects/duncombe
    #buckettags = { 'ioos-cloud-sandbox':'IOOS-cloud-sandbox' }
    #buckettags = { 'rps-glos':'RPS-GLOS' }
# done
# backup/Home/projects/acrosby
# backup/Home/projects/dpsnowden
# COMTUT


    buckettags = { 'ioos-comt':'IOOS-COMT'}
# Test
#    buckettags = { 'rps-glos-config':'RPS-GLOS' }
# Skip[ tds/content/thredds

    # skip these
    # Testp = re.compile('(tds/content/thredds|nginx)')
    p = re.compile('(backup/Home/projects/acrosby|backup/Home/projects/dpsnowden|COMTUT)')

    for bucket in buckettags.keys():
        project = buckettags[bucket]
        print(f"bucket: {bucket} Project: {project}")

        # get all keys
        page_iterator = paginator.paginate(Bucket=bucket)

        newtag = { 'Key': 'Project', 'Value': project }
        for page in page_iterator:
            print(f"KeyCount: {page['KeyCount']}  :  IsTruncated: {page['IsTruncated']}")

            for content in page['Contents']:
                key = content['Key']
                if p.match(key): 
                  print(f"bucket/key: {bucket}/{key} ------- Skipped")
                else:
                  print(f"bucket/key: {bucket}/{key}")
                  #print(f"Tagging {key}")
                  s3.put_object_tagging(Bucket=bucket, Key=key, Tagging={'TagSet': [ newtag ] })


if __name__ == '__main__':
  main()

#ioos-cloud : IsTruncated: True
#ioos-cloud-sandbox : IsTruncated: True
#ioos-comt : IsTruncated: True
#ioos-eds : IsTruncated: True
#ott-radial : IsTruncated: True
