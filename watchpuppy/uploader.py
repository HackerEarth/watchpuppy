import os

UPLOAD_CMD = 's3cmd -r -v --guess-mime-type --acl-public put {local_file_path} s3://{bucket_name}/{key}'

class S3Uploader(object):

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def  upload(self, local_file_path, s3_key):
        cmd = UPLOAD_CMD.format(local_file_path=local_file_path,
                bucket_name=self.bucket_name, key=s3_key)
        print "Uploading"
        os.system(cmd)


