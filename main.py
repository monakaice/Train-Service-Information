#!/ust/bin/env python
# -*- coding: utf-8 -*-


from configparser import ConfigParser
from datetime import datetime
from scraping import JRService
from threading import Timer
from time import sleep
from sys import exit
from my_util import logger
import requests


config = ConfigParser()
config.read('./.env')
thread_time_min = config.getint('settings', 'watch_interval_min')
thread_time_sec = thread_time_min * 60
services = config.items('jr_services')


def push_slack_chat(name, message):
    url = config.get('settings', 'post_url')
    token = config.get('settings', 'token')
    channel = config.get('settings', 'channel')
    data = {
        'token': token,
        'channel': channel,
        'username': name,
        'text': message
    }
    requests.post(url, data=data)


def push_webex_chat(name, message):
    url = config.get('settings', 'webex_post_url')
    auth = config.get('settings', 'webex_auth')
    room_id = config.get('settings', 'webex_room_id')
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer ' + auth
    }
    payload = {
        'roomId': room_id,
        'text': name + '\n' + message
    }
    requests.post(url, json=payload, headers=headers)


def scrape_service():
    try:
        for key, url in services:
            scraper = JRService(url)
            data = scraper.get_data()

            last_posting_datetime_str = config.get('posting_datetime', key)
            last_posting_datetime = datetime.strptime(last_posting_datetime_str, '%Y-%m-%d %H:%M')

            last_in_trouble = config.getboolean('in_trouble', key)
            if data['in_trouble'] and (data['posting_datetime'] <= last_posting_datetime):
                continue
            elif (data['in_trouble'] and not last_in_trouble)\
                    or (last_in_trouble and not data['in_trouble'])\
                    or data['in_trouble'] and (data['posting_datetime'] > last_posting_datetime):

                # push_slack_chat(data['route_name'], data['message'])
                push_webex_chat(data['route_name'], data['message'])

                in_trouble_str = 'True' if data['in_trouble'] else 'False'
                config.set('in_trouble', key, in_trouble_str)
                if data['in_trouble']:
                    posting_datetime_str = data['posting_datetime'].strftime('%Y-%m-%d %H:%M')
                    config.set('posting_datetime', key, posting_datetime_str)

                config.write(open('./.env', 'w'))

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
