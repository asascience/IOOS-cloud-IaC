import boto3
from botocore.exceptions import ClientError

from services import CloudStorage

debug = False

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)

class S3Storage(CloudStorage.CloudStorage):

  def __init__(self, configfile):
    print('init stub')


