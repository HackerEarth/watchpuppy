import logging
import settings

UPLOADER_LOGS = []

class WatchPuppyLogHandler(logging.StreamHandler):
    def emit(self, record):
        log = self.format(record)
        UPLOADER_LOGS.append(log)

def get_logger(name='WatchPuppy'):
    #handler = logging.FileHandler(settings.UPLOADER_LOG_FILE)
    handler = WatchPuppyLogHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
    handler.setFormatter(formatter)
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    return log


