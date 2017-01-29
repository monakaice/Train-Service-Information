#!/ust/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from datetime import datetime
from urllib import request
from my_util import logger, dict_to_str


class Scraper(metaclass=ABCMeta):
    def __init__(self, url):
        self._url = url

    @abstractmethod
    def get_data(self):
        pass

    def __make_proxy_url(self):
        pass


class JRService(Scraper):
    def __init__(self, url):
        super().__init__(url)

    def get_data(self):
        html = request.urlopen(self._url).read()
        soup = BeautifulSoup(html, 'lxml')

        # 路線情報
        route_element = soup.find('div', {'id': 'main'}).find('div', {'class': 'mainWrp'}).find('div', {'class': 'labelLarge'})
        route_name = route_element.find('h1', {'class': 'title'}).find(text=True, recursive=False)
        update_time_str = route_element.find('span', {'class': 'subText'}).find(text=True, recursive=False)

        # 1900年になってしまうため年の補完を行う。
        year = datetime.today().year
        convert_str = '%d年%s' % (year, update_time_str)
        update_time = datetime.strptime(convert_str, '%Y年%m月%d日 %H時%M分更新')

        # 運行情報
        status_element = soup.find('div', {'id': 'mdServiceStatus'})
        information = status_element.find('p').find(text=True, recursive=False)
        posting_element = status_element.find('p').find('span')
        posting_date = ''
        if posting_element is not None:
            posting_date = posting_element.find(text=True, recursive=False)

        message = information + posting_date

        trouble_class = status_element.find('dd', {'class': 'trouble'})
        in_trouble = False
        if trouble_class is not None:
            in_trouble = True

        data = {
            'route_name': route_name,
            'update_time': update_time,
            'message': message,
            'in_trouble': in_trouble
        }

        logger.info(dict_to_str(data))

        return data
