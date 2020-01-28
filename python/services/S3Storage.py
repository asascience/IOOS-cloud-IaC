import os
import logging

import boto3
from botocore.exceptions import ClientError

from services import CloudStorage

debug = False

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)

class S3Storage(CloudStorage.CloudStorage):

  def __init__(self):
    print('init stub')


  def upload_file(self, filename: str, bucket: str, key: str, public: bool = False):

    s3 = boto3.client('s3')
    try:
      if public:
        s3.upload_file(filename, bucket, key, ExtraArgs={'ACL': 'public-read'})
      else:
        s3.upload_file(filename, bucket, key)
    except ClientError as e:
      log.error(e)
      raise Exception from e
