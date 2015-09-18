import pyinotify
import uploader
import asyncore
import threading

DIR_TO_WATCH = '/home/praveen/webapps/django/mycareerstack/media'

ROOT = '/home/praveen/webapps/django/mycareerstack/'

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_DELETE(self, event):
        print "Removing:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "Closinsssc", event.pathname
        print "Uploading to S3"
        upl = uploader.S3Uploader('he-bigdata-test')
        local_file_path = event.pathname
        s3_key = local_file_path.replace(ROOT, '')
        thread = threading.Thread(target=upl.upload, args=(local_file_path,
            s3_key))
        thread.start()



watch_manager = pyinotify.WatchManager()


DIR_TO_WATCH = '/home/praveen/webapps/django/mycareerstack/media'

watch_manager.add_watch(DIR_TO_WATCH, pyinotify.ALL_EVENTS, rec=True)

handler = EventHandler()


notifier = pyinotify.AsyncNotifier(watch_manager, handler)


try:
    print "Starting loop notifier"
    notifier.loop(daemonize=True, pid_file='/tmp/pyinotify.pid',
        stdout='/tmp/pyinotify.log')
except Exception:
    import traceback
    print traceback.format_exc()
