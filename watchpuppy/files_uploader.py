import datetime
import logging
import logger
import optparse
import os
import subprocess
import threading

import settings
import uploader

from models import FileInfo, UploadStatus, FileUploaderLog

from logger import get_logger


log = get_logger(__name__)


UPLOAD_CMD = 's3cmd -r -v --guess-mime-type --acl-public put {local_file_path} s3://{bucket_name}/{key}'


def upload_file_to_s3(local_file_path, s3_key):

    log.debug("Requested upload of file %s to %s", local_file_path, s3_key)

    debug_info = ''
    valid_upload = True
    if not os.path.exists(local_file_path):
        debug_info = "File not found on the local file system "
        valid_upload = False
        log.debug("Invalid Upload: File not found on local file system "+local_file_path)

    if not valid_upload:
        file_info = FileInfo.objects.get(file_path=local_file_path)
        file_info.debug_info = debug_info
        file_info.upload_status = UploadStatus.FAILED
        file_info.save()
        return

    cmd = UPLOAD_CMD.format(local_file_path=local_file_path,
            bucket_name=settings.S3_BUCKET, key=s3_key)
    log.debug("Uploading file " + local_file_path)
    out, err = subprocess.Popen(cmd, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    file_info = FileInfo.objects.get(file_path=local_file_path)

    if "stored as" in out:
        file_info.upload_status = UploadStatus.UPLOAD_SUCCESSFUL
        log.debug("File %s uploaded to %s", local_file_path, s3_key)
    else:
        file_info.upload_status = UploadStatus.FAILED
        file_info.debug_info = err
    file_info.save()

def get_s3_key_for_file_path(file_path):
    s3_key = file_path.replace(settings.FILESYSTEM_ROOT, '')
    return s3_key

def async_upload_file( file_path):

    local_file_path = file_path
    s3_key = get_s3_key_for_file_path(local_file_path)

    thread = threading.Thread(target=upload_file_to_s3, args=(local_file_path,
        s3_key))
    return thread

def check_file_exists_in_s3(s3_key, exists_dict={}):
    cmd = "s3cmd info s3://{s3_key}".format(s3_key=s3_key)
    exists = True
    try:
        out, err = subprocess.Popen("s3cmd info {s3_key}".format(s3_key=s3_key), shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        if not out and err:
            # False for any error
            exists = False
    except Exception:
        exists = False
    exists_dict[s3_key] = exists
    return exists_dict

def check_files_exist_in_s3(s3_keys):
    exists_dict = {}
    threads = [threading.Thread(target=check_file_exists_in_s3, args=(s3_key,
        exists_dict))
        for s3_key in s3_keys]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    return exists_dict

def upload_files(files):

    log.debug("Will spawn %s threads "%files.__len__())
    log.debug("Upload files started ")

    uploader_threads = [async_upload_file(file_path) for file_path in files]
    for uploader_thread in uploader_threads:
        uploader_thread.start()

    for uploader_thread in uploader_threads:
        uploader_thread.join()

    log.debug("Upload files finished")


def determine_files_to_upload(interval=5*60, time_buffer=60,
        upload_status=[UploadStatus.NOT_UPLOADED, UploadStatus.FAILED],
        overwrite_in_s3=False):
    """Determines which files have to uploaded to S3 if the files
    are not present in S3.
    """

    interval = interval + time_buffer
    end_time = datetime.datetime.now() - datetime.timedelta(seconds=120)

    start = end_time - datetime.timedelta(seconds=interval)

    log.debug("Collecting files created between %s and %s", start, end_time)

    files_info = FileInfo.objects.filter(created__gte=start,
            upload_status__in=upload_status)

    files = files_info.values_list('file_path')
    log.debug("Found %s files ", files.__len__())

    if overwrite_in_s3:
        # we intend to overwrite the files in S3
        log.debug("Option to overwrite files in S3 passed. Returning all files")
        return files

    s3_keys = {file_path: get_s3_key_for_file_path(file_path) for file_path in
            files}

    s3_exists_keys = check_files_exist_in_s3(s3_keys.values())

    non_existing_files = []
    for file_path in files:
        s3_key = s3_keys.get(file_path)
        key_exists = s3_exists_keys.get(s3_key)
        if not key_exists:
            non_existing_files.append(file_path)
    log.debug("Found %s non existing files in S3", non_existing_files.__len__())
    return non_existing_files

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i', '--interval', action='store', dest='interval')

    options, remainder = parser.parse_args()
    interval = options.interval

    uploader_start_time = datetime.datetime.now()
    uploader_successful = FileUploaderLog.SUCCESSFUL
    logs = []
    tb = None
    files = []
    try:
        files = determine_files_to_upload()
        upload_files(files)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        uploader_successful = FileUploaderLog.FAILED

    uploader_end_time = datetime.datetime.now()
    logs = logger.UPLOADER_LOGS
    if tb:
        logs.append(tb)
    uploader_log = FileUploaderLog(
            files_uploaded=files,
            start_time=uploader_start_time,
            end_time=uploader_end_time,
            run_status=uploader_successful,
            logs=logs)
    uploader_log.save()

if __name__ == '__main__':
    main()
