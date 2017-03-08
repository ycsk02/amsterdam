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
import re

class ArslanlarsporSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #     }
    # }
    name = "Arslanlarspor"
    allowed_domains = ["arslanlarspor.com",]

    start_urls = ['http://arslanlarspor.com/index.php?route=product/category&path=64',]

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//ul[@class="pagination"]/li/a',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//h3[@class="name"]/a/@href')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                product_page_url = product.extract()
                logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                #yield Request(product_page_url,callback = self.parse_page,dont_filter=True)
                yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%product.xpath('.//h3/a/@href')[0].extract())

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//h1[@class="title-product"]/text()')[0].extract()
        try:
            item['info'] = sel.xpath('//div[@id="tab-description"]')[0].extract()
        except:
            item['info'] = ''
        try:
            item['category'] = "FORMALAR"
        except:
            item['category'] = ''
        item['domain'] = 'arslanlarspor.com'
        try:
            item['brand'] = 'FORMA'
        except:
            item['brand'] = ''
        try:
            price = sel.xpath('//span[@class="price-new"]/text()')[0].extract().strip()[1:].replace(',','.')
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = '0'
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'USD'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        image = sel.xpath('//img[@id="image"]/@src')[0].extract()
        item['image_urls'].append(image)
        pictures.append({'sml':image,'lrg':image,'zoom':image})

        item['pictures'] = json.dumps(pictures)
        if not item['pictures']:
            logging.log(logging.WARNING, "This product pictures is null: %s"%item['url'])
        item['targetId'] = 'arslanlarspor.com' + sel.xpath('//input[@name="product_id"]/@value')[0].extract()

        #以下未取到数据
        item['weight'] = '0'
        item['size'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        item['color'] = ''
        return item
