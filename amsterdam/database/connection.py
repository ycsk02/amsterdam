# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from amsterdam import settings

from elasticsearch import Elasticsearch

# # db settings
# dbuser = 'root'
# #dbpass = 'nopass'
# #dbhost = 'localhost'
# dbpass = 'root'
# dbhost = '192.168.1.120'
# dbname = 'spider'

engine = create_engine("mysql://%s:%s@%s/%s?charset=utf8&use_unicode=0"
                       %(settings.DBUSER, settings.DBPASS, settings.DBHOST, settings.DBNAME),
                       echo=False,
                       pool_recycle=1800)

db = scoped_session(sessionmaker(autocommit=False,
                                 autoflush=False,
                                 bind=engine))
Base = declarative_base()

#es_servers = '192.168.1.192:9200'
# es_servers = '192.168.1.120:9200'
es = Elasticsearch(hosts=settings.EC_SERVERS,timeout=60)
