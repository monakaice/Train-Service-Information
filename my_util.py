#!/ust/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger, Formatter, StreamHandler, basicConfig, DEBUG

basicConfig(format='[%(asctime)s], %(levelname)s, %(message)s', level=DEBUG)

logger = getLogger()
__stream_handler = StreamHandler()
__formatter = Formatter('[%(asctime)s], %(levelname)s, %(message)s')
__stream_handler.setFormatter(__formatter)
__stream_handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(__stream_handler)


def dict_to_str(target):
    string = ''.join('{}:{}\n'.format(key, val) for key, val in target.items())
    return string
