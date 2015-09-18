import optparse
import logging

from watchers.media import MediaFilesEventWatcher

logger = logging.getLogger()


REGISTERED_WATCHERS = {
    MediaFilesEventWatcher.__name__ : MediaFilesEventWatcher
}



def main():
    print "Here"
    parser = optparse.OptionParser()
    parser.add_option('-w', '--watcher', action='store', dest='watcher')
    parser.add_option('-d', '--daemonize', action='store_false', default=False,
            dest='daemonize')
    parser.add_option('-s', '--settings', action='store', dest='settings')

    options, remainder = parser.parse_args()

    watcher_name = options.watcher
    print watcher_name
    logger.debug("Watcher to start " + watcher_name)
    watcher_class = REGISTERED_WATCHERS.get(watcher_name)
    if watcher_class is None:
        raise Exception("No watcher found for class " + watcher_class)

    daemonize = options.daemonize
    settings_module = __import__(options.settings)
    watcher = watcher_class(settings_module, daemonize=daemonize)
    watcher.start_watcher()

if __name__ == '__main__':
    main()
main()
