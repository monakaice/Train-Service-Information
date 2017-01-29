#!/ust/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta
import sqlalchemy as sqlal
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from configparser import ConfigParser
from my_util import logger
import requests


config = ConfigParser()
config.read('./.env')

connectionString = config.get('settings', 'connection_string')
engine = sqlal.create_engine(connectionString, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class OperationInformation:
    def __init__(self):
        self.__session = Session()

    def push_chat(self, service_url, data):
        route_name = data['route_name']
        message = data['message']
        in_trouble = data['in_trouble']
        update_time = data['update_time']
        self.__register(route_name, message, service_url, in_trouble, update_time)

        if in_trouble:
            logger.debug('トラブル中')
            self.__push_slack_chat(message)
        elif self.__out_of_trouble():
            logger.debug('トラブル解除')
            self.__push_slack_chat(message)
        else:
            logger.debug('トラブル無し')
            pass

    def __register(self, route_name, message, service_url, in_trouble, update_time):
        scraping = _Scraping(route_name=route_name, message=message, service_url=service_url
                             , in_trouble=in_trouble, update_time=update_time)
        self.__session.add(scraping)
        self.__delete_old_scraping(service_url)
        self.__session.commit()

    def __delete_old_scraping(self, service_url):
        filter_time = datetime.utcnow() + relativedelta(months=1)
        filter_time_str = filter_time.strftime('%Y/%m/%d %H:%M:%S')
        logger.debug('データ削除：' + filter_time_str + ' 以降のデータ')
        self.__session.query(_Scraping)\
            .filter(_Scraping.service_url == service_url)\
            .filter(_Scraping.create_time > filter_time)\
            .delete()

    def __out_of_trouble(self):
        first_info = self.__session.query(_Scraping).order_by(_Scraping.create_time.desc()).first()
        if first_info is None:
            return False
        elif first_info.in_trouble:
            return True
        else:
            return False

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


class _Scraping(Base):
    __tablename__ = 'jr_service_scrapings'

    seq = sqlal.Column(sqlal.Integer, primary_key=True)
    route_name = sqlal.Column(sqlal.String(200), nullable=False)
    message = sqlal.Column(sqlal.String(200), nullable=False)
    service_url = sqlal.Column(sqlal.String(1024), nullable=False)
    in_trouble = sqlal.Column(sqlal.BOOLEAN, default=False, nullable=False)
    create_time = sqlal.Column(sqlal.DateTime, default=datetime.utcnow, nullable=False)
    update_time = sqlal.Column(sqlal.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        string = "<%s(%d, %s, %s, %s, %s, %s, %s)>" % (self.__class__
                                                       , self.seq
                                                       , self.route_name
                                                       , self.message
                                                       , self.service_url
                                                       , self.in_trouble
                                                       , self.create_time
                                                       , self.update_time)
        return string


Base.metadata.create_all(engine, checkfirst=True)