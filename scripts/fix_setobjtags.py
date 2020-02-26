#!/usr/bin/python3

import re

import boto3

#def setobjtag (bucket: str, project: str):


def main():

    s3 = boto3.client('s3')
    paginator = s3.get_paginator('list_objects_v2')

    # FIX THIS    'eds-snowball':'EDS',
    # Redo the following
    # eds-snowball/destfolder/RADIALS/OSU/YHL1/
    # eds-snowball/destfolder/RADIALS/OSU/YHS2/

    # destfolder/RADIALS/Rutgers
    # destfolder/RADIALS/SC
    # destfolder/RADIALS/SFSU
    # destfolder/RADIALS/SIO
    # destfolder/RADIALS/SIT
    # destfolder/RADIALS/SKIO
    # destfolder/RADIALS/SLO

    buckettags = {
        'eds-snowball':'EDS',
    }

    # Redo these
    #p = re.compile('(destfolder/RADIALS/OSU/YHL1/|destfolder/RADIALS/OSU/YHS2)')  # DONE
    p = re.compile('( destfolder/RADIALS/Rutgers| destfolder/RADIALS/SC| destfolder/RADIALS/SFSU| destfolder/RADIALS/SIO| 
                      destfolder/RADIALS/SIT| destfolder/RADIALS/SKIO| destfolder/RADIALS/SLO)')


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
                      print(f"bucket/key: {bucket}/{key}")
                      s3.put_object_tagging(Bucket=bucket, Key=key, Tagging={'TagSet': [ newtag ] })
                    else:
                      print(f"bucket/key: {bucket}/{key} ------- Skipped")


if __name__ == '__main__':
  main()

#ioos-cloud : IsTruncated: True
#ioos-cloud-sandbox : IsTruncated: True
#ioos-comt : IsTruncated: True
#ioos-eds : IsTruncated: True
#ott-radial : IsTruncated: True
