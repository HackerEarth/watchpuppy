import datetime
import pyinotify
import uploader
import asyncore
import threading
import os

import logging
import settings

from models import FileInfo

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class MediaFilesEventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        super(MediaFilesEventHandler, self).__init__()

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        thread = threading.Thread(target=self.callback, args=(event,))
        thread.start()

    def callback(cls, event):
        local_file_path = event.pathname
        s3_key = local_file_path.replace(settings.FILESYSTEM_ROOT, '')
        created = datetime.datetime.now()
        log_line = "Saving info Local file path: %s  s3_key: %s "%(local_file_path, s3_key)
        logger.debug(log_line)

        file_info = FileInfo(file_path=local_file_path, s3_key=s3_key,
                created=created)

        query_fields = {'file_path': local_file_path}
        update_fields = {
            'file_path': local_file_path,
            's3_key': s3_key,
            'created': created
        }
        file_info.create_or_update(query_fields=query_fields, update_fields=update_fields)

class MediaFilesEventWatcher(object):

    def __init__(self, handler=MediaFilesEventHandler,
            daemonize=False):
        self.handler = handler
        self.daemonize = daemonize

    def get_notifier(self):
        watch_manager = pyinotify.WatchManager()

        logger.debug("Will watch directory " + settings.MEDIA_ROOT)

        watch_manager.add_watch(settings.MEDIA_ROOT, pyinotify.ALL_EVENTS, rec=True)
        handler = self.handler()
        notifier = pyinotify.AsyncNotifier(watch_manager, handler)
        return notifier


    def start_watcher(self):
        notifier = self.get_notifier()
        pid_file = settings.PID_FILE
        stdout_file = settings.STD_OUT_FILE
        try:
            logger.debug("Starting server")
            notifier.loop(daemonize=self.daemonize,
                    pid_file=pid_file,
                    stdout=stdout_file)
        except Exception:
            import traceback
            print traceback.format_exc()
        finally:
            if os.path.exists(pid_file):
                os.remove(pid_file)


