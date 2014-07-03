from threading import Thread
from time import sleep
import activefolders.controllers.transfers as transfers
import activefolders.controllers.exports as exports
import activefolders.controllers.results as results
import activefolders.conf as conf

class Monitor(Thread):
    SLEEP_TIME = conf.settings['dtnd']['update_interval']

    def run(self):
        while True:
            transfers.update_all()
            exports.update_all()
            results.update_all()
            sleep(self.SLEEP_TIME)