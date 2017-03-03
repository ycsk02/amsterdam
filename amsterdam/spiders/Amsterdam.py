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

class AmsterdamSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #     }
    # }
    name = "Amsterdam"
    allowed_domains = ["file:///home/sukai"]

    start_urls = ['file:///home/sukai/product02032017withurl.csv',]

    def parse(self,response):
        with open('/home/sukai/product02032017withurl.csv','rb') as csvfile:
            reader = csv.DictReader(csvfile,delimiter=',',quotechar='"')
            for row in reader:
                if len(row) != 0:
                    item = ProductItem()
                    item['url'] = row['Product-link']
                    logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
                    item['name'] = row['post_title']
                    item['info'] = row['post_content']
                    item['category'] = '|'.join(row['tax:product_cat'].split('|')[0:2])
                    item['domain'] = 'body.amsterdam'
                    item['brand'] = ''
                    item['price'] = row['regular_price']
                    item['oldprice'] = '0'
                    item['currency'] = 'EUR'
                    item['createdTime'] = int(time.time())
                    item['lastUpdatedTime'] = int(time.time())
                    item['image_urls'] = [row['images']]
                    pictures = []
                    pictures.append({'sml':row['images'],'lrg':row['images'],'zoom':row['images']})
                    item['pictures'] = json.dumps(pictures)
                    item['targetId'] = 'body.amsterdam' + row['Reference #']
                    item['weight'] = row['weight']
                    #以下未取到数据
                    item['color'] = ''
                    item['size'] = ''
                    item['mainPicture'] = ''
                    item['lpictures'] = ''
                    yield item
