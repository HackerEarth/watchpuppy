from mongoengine import register_connection

DEBUG = True

FILESYSTEM_ROOT = '/home/praveen/webapps/django/mycareerstack/'

MEDIA_ROOT = FILESYSTEM_ROOT + 'media/'

S3_BUCKET = 'he-bigdata-test'

PID_FILE = '/tmp/watchpuppy.pid'

STD_OUT_FILE = '/tmp/watchpuppy.stdout.log'

UPLOADER_LOG_FILE = '/tmp/watchpuppy_file_uploader.log'

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

MONGODB_CONN_ALIASES = ['watchpuppy']

for alias in MONGODB_CONN_ALIASES:
    register_connection(alias, alias,
        host=MONGODB_HOST, port=MONGODB_PORT)
