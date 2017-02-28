# -*- coding: utf-8 -*-
import scrapy
import time
import json
import requests
import logging
from scrapy.selector import Selector
# from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
# from scrapy.http import Request
from decimal import Decimal
from amsterdam.items import ProductItem
#import lxml.etree as ET
import csv

class BybojSpider(CrawlSpider):
    name = "Byboj"
    allowed_domains = ["file:///home/sukai"]
    start_urls = ['file:///home/sukai/BOJProductList.csv',]
    # custom_settings = {
    #     'ITEM_PIPELINES': {}
    # }

    def parse(self,response):
        with open('/home/sukai/BOJProductList_copy.csv','r') as csvfile:
            spamreader = csv.reader(csvfile,delimiter=',',quotechar='"')
            for product in spamreader:
                if len(product) != 0:
                    item = ProductItem()
                    item['url'] = product[9]
                    item['name'] = product[0]
                    item['info'] = product[7]
                    item['category'] = product[6]
                    item['domain'] = 'byboj.cn'
                    try:
                        item['brand'] = product[5]
                    except:
                        item['brand'] = ''
                    item['price'] = Decimal(product[1].replace(',',''))
                    item['oldprice'] = Decimal(0)
                    item['currency'] = 'RMB'
                    item['createdTime'] = int(time.time())
                    item['lastUpdatedTime'] = int(time.time())
                    pictures = []
                    item['image_urls'] = []
                    item['image_urls'].append(product[8])
                    pictures.append({'sml':product[8],'lrg':product[8],'zoom':product[8]})
                    item['pictures'] = json.dumps(pictures)
                    item['targetId'] = 'byboj.cn'+product[4]
                    #以下未取到数据
                    item['size'] = ''
                    item['color'] = ''
                    item['mainPicture'] = ''
                    item['lpictures'] = ''
                    item['weight'] = 0
                    yield item
