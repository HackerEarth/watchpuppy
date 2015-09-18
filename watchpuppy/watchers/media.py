import pyinotify
import uploader
import asyncore
import threading

import logging

logger = logging.getLogger()


class MediaFilesEventHandler(pyinotify.ProcessEvent):
    def __init__(self, settings):
        self.settings = settings
        super(MediaFilesEventHandler, self).__init__()

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "Uploading to S3"
        upl = uploader.S3Uploader(self.settings.S3_BUCKET)
        local_file_path = event.pathname
        s3_key = local_file_path.replace(self.settings.FILESYSTEM_ROOT, '')
        thread = threading.Thread(target=upl.upload, args=(local_file_path,
            s3_key))
        thread.start()


class MediaFilesEventWatcher(object):
    def __init__(self, settings, handler=MediaFilesEventHandler,
            daemonize=False):
        self.handler = handler
        self.settings = settings
        self.daemonize = daemonize

    def get_notifier(self):
        watch_manager = pyinotify.WatchManager()
        print self.settings.MEDIA_ROOT

        logger.debug("Will watch directory " + self.settings.MEDIA_ROOT)

        watch_manager.add_watch(self.settings.MEDIA_ROOT, pyinotify.ALL_EVENTS, rec=True)
        handler = self.handler(self.settings)
        notifier = pyinotify.AsyncNotifier(watch_manager, handler)
        return notifier


    def start_watcher(self):
        notifier = self.get_notifier()
        pid_file = self.settings.PID_FILE
        stdout_file = self.settings.STD_OUT_FILE
        try:
            logger.debug("Starting server")
            print "Starting server"
            notifier.loop(daemonize=self.daemonize,
                    pid_file=pid_file,
                    stdout=stdout_file)
        except Exception:
            import traceback
            print traceback.format_exc()
