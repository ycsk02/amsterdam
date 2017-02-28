# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, DateTime,Numeric,Text,BigInteger
from amsterdam.database.connection import Base

class Product(Base):
    __tablename__ = 't_unsettled_product'
    id = Column(Integer, primary_key=True)
    name = Column(String(125))
    info = Column(String(9096))
    category = Column(String(120))
    domain = Column(String(64))
    price = Column(Numeric)
    oldprice = Column(Numeric)
    currency = Column(String(6))
    url = Column(String(2048))
    brand = Column(String(64))
    color = Column(String(24))
    size = Column(String(64))
    targetId = Column(String(128))
    mainPicture = Column(String(512))
    pictures = Column(String(7869))
    lpictures = Column(Text)
    createdTime = Column(BigInteger)
    lastUpdatedTime = Column(BigInteger)
    updatedTimeBeforeLast = Column(BigInteger)
    weight = Column(Numeric)

class TProduct(Base):
    __tablename__ = 't_product'
    id = Column(Integer, primary_key=True)
    name = Column(String(125))
    info = Column(String(9096))
    price = Column(String(20))
    oldprice = Column(String(20))
    currency = Column(String(6))
    url = Column(String(2048))
    brand = Column(String(64))
    mainPicture = Column(String(512))
    pictures = Column(Text)
    domain = Column(String(64))
    channelCode = Column(String(40))
    tariffCode = Column(String(40))
    tags = Column(String(200))
    targetId = Column(String(11))
    createdTime = Column(BigInteger)
    lastUpdatedTime = Column(BigInteger)
    pid = Column(String(48))
    weight = Column(Numeric)

#    def __init__(self, id=None, title=None, url=None, date=None):
#        self.id = id
#        self.title = title
#        self.url = url
#        self.date = date

#    def __repr__(self):
#        return "<AllData: id='%d', title='%s', url='%s', date='%s'>" % (self.id, self.title, self.url, self.date)
