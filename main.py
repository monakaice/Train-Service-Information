#!/ust/bin/env python
# -*- coding: utf-8 -*-


from configparser import ConfigParser
from scraping import JRService
from threading import Timer
from time import sleep
from sys import exit
from my_logic import OperationInformation
from my_util import logger


config = ConfigParser()
config.read('./.env')
thread_time_min = config.getint('settings', 'watch_interval_min')
thread_time_sec = thread_time_min * 60
services = config.items('jr_services')


def scrape_service():
    try:
        for key, url in services:
            scraper = JRService(url)
            data = scraper.get_data()
            operation = OperationInformation()
            operation.push_chat(url, data)
    except Exception as e:
        logger.error(e.with_traceback())
    finally:
        thread = Timer(thread_time_sec, scrape_service)
        thread.start()


if __name__ == '__main__':

    scrape_service()

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        exit(0)
