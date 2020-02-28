#!/usr/bin/python3

import re

import boto3

#def setobjtag (bucket: str, project: str):



def main():

    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    donebukets = {
        'apptio-eds-108193140983':'EDS',
        'eds-master':'EDS' }


    # FIX THIS ONE        'eds-snowball':'EDS', DONE
    # eds-snowball/destfolder/RADIALS/OSU/YHL1/ DONE
    # next is:
    # eds-snowball/destfolder/RADIALS/OSU/YHS2/ DONE
    # :end of RADIALS/OSU


    buckettags = {
        'edsapilogs':'EDS',
        'hycomglobal':'EDS',
        'radials':'EDS/OTT-RADIALS' }

    # Skip these
    #p = re.compile('(backup/Home/projects/acrosby|backup/Home/projects/dpsnowden|COMTUT)')
    p = re.compile('dontmatchanything123456')

    for bucket in buckettags.keys():
        project = buckettags[bucket]
        print(f"bucket: {bucket} Project: {project}")

        # get all keys
        page_iterator = paginator.paginate(Bucket=bucket)

        newtag = { 'Key': 'Project', 'Value': project }
        for page in page_iterator:
            keycount = page['KeyCount']
            print(f"KeyCount: {keycount}  :  IsTruncated: {page['IsTruncated']}")

            if keycount != 0:
                for content in page['Contents']:
                    key = content['Key']
                    if p.match(key): 
                      print(f"bucket/key: {bucket}/{key} ------- Skipped")
                    else:
                      print(f"bucket/key: {bucket}/{key}")
                      s3.put_object_tagging(Bucket=bucket, Key=key, Tagging={'TagSet': [ newtag ] })


if __name__ == '__main__':
  main()

#ioos-cloud : IsTruncated: True
#ioos-cloud-sandbox : IsTruncated: True
#ioos-comt : IsTruncated: True
#ioos-eds : IsTruncated: True
#ott-radial : IsTruncated: True
