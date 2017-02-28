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
import lxml.etree as ET

class SkinstoreSpider(CrawlSpider):
    name = "Skinstore"
    allowed_domains = ["file:///home/sukai"]
    start_urls = ['file:///home/sukai/SkinStore_com-Product_Catalog_1.xml',]

    def parse(self,response):
        root = ET.fromstring(response.body)
        for product in root:
            item = ProductItem()
            if product.find('instock').text == 'yes':
                item['url'] = product.find('buyurl').text
                item['name'] = product.find('name').text
                item['info'] = product.find('description').text
                item['category'] = product.find('advertisercategory').text
                item['domain'] = 'www.skinstore.com'
                try:
                    item['brand'] = product.find('manufacturer').text
                except:
                    item['brand'] = ''
                item['price'] = Decimal(product.find('price').text)
                item['oldprice'] = Decimal(product.find('retailprice').text)
                item['currency'] = 'USD'
                item['createdTime'] = int(time.time())
                item['lastUpdatedTime'] = int(time.time())
                pictures = []
                item['image_urls'] = []
                item['image_urls'].append(product.find('imageurl').text)
                pictures.append({'sml':product.find('imageurl').text.replace('960/960','300/300'),'lrg':product.find('imageurl').text.replace('960/960','600/600'),'zoom':product.find('imageurl').text})
                item['pictures'] = json.dumps(pictures)
                item['targetId'] = 'www.skinstore.com'+product.find('sku').text
                #以下未取到数据
                item['size'] = ''
                item['color'] = ''
                item['mainPicture'] = ''
                item['lpictures'] = ''
                item['weight'] = 0
                yield item
