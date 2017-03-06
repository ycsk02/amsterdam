# -*- coding: utf-8 -*-
import scrapy
import time
import json
import requests
import logging
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from decimal import Decimal
from amsterdam.items import ProductItem
from amsterdam import settings
import csv
import lxml.etree as ET

class PrettyGirlSpider(CrawlSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            'amsterdam.pipelines.MyImagePipeline': 200,
            'amsterdam.pipelines.AddTablePipeline': 400,
            'amsterdam.pipelines.AddElasticsearchPipeline':900,
            'amsterdam.pipelines.UpdatePricePipeline':1200,
        }
    }
    name = "PrettyGirl"
    allowed_domains = ["file:///home/sukai"]

    start_urls = ['file:///home/sukai/THAIexport.xml',]

    def parse(self,response):
        root = ET.fromstring(response.body)
        for product in root[1:]:
            item = ProductItem()
            if product.find('STOCK_STATUS').text == 'In Stock':
                item['url'] = product.find('PRODUCT_URL').text
                item['name'] = product.find('NAME').text
                item['info'] = product.find('DESCRIPTION').text
                item['category'] = "|".join([x.text for x in product.find('CATEGORIES').findall('CATEGORY')])
                item['domain'] = 'www.prettygirl.asia'
                try:
                    item['brand'] = product.find('MANUFACTURER').text
                except:
                    item['brand'] = ''
                item['price'] = Decimal(product.find('PRICE').text[1:])
                item['oldprice'] = '0'
                item['currency'] = 'USD'
                item['createdTime'] = int(time.time())
                item['lastUpdatedTime'] = int(time.time())
                pictures = []
                item['image_urls'] = [x.text.strip() for x in product.find('IMAGES')]
                pictures = [ {'sml':x.text.strip(),'lrg':x.text.strip(),'zoom':x.text.strip()} for x in product.find('IMAGES')]
                item['pictures'] = json.dumps(pictures)
                item['targetId'] = 'www.prettygirl.asia'+product.find('PRODUCT_ID').text
                convert_kg = lambda x: '{}'.format(x/1000 + 0.3)
                item['weight'] = convert_kg(float(product.find('WEIGHT').text))
                #以下未取到数据
                item['size'] = ''
                item['color'] = ''
                item['mainPicture'] = ''
                item['lpictures'] = ''
                yield item
