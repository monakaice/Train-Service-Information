#!/ust/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from my_util import logger
import requests


config = ConfigParser()
config.read('./.env')

connectionString = config.get('settings', 'connection_string')


class OperationInformation:
    def __init__(self):
        pass

    def push_chat(self, data):
        message = data['message']
        in_trouble = data['in_trouble']

        if in_trouble:
            logger.debug('in trouble')
            self.__push_slack_chat(message)
        else:
            logger.debug('non trouble')
            pass

    @staticmethod
    def __push_slack_chat(message):
        url = config.get('settings', 'post_url')
        token = config.get('settings', 'token')
        channel = config.get('settings', 'channel')
        username = config.get('settings', 'username')
        data = {
            'token': token,
            'channel': channel,
            'username': username,
            'text': message
        }
        requests.post(url, data=data)
