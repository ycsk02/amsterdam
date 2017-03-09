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

class UcareSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #         # #'amsterdam.pipelines.CSVPipeline':1500,
    #     }
    # }
    name = "Ucare"
    allowed_domains = ["u-care.com.au","shopify.com"]

    # def get_starturls():
    #     response_page = requests.get('http://www.kiddies-kingdom.com/')
    #     sel_page = Selector(response_page)
    #     categorylink = sel_page.xpath('//a[contains(@class,"menulinks_mm ma_level_2")]/@href').extract()
    #     return categorylink
    #
    # start_urls = get_starturls()
    start_urls = ['http://www.u-care.com.au/collections/all',]

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//div[@class="pagination wide"]//a',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//ul[@id="coll-product-list"]/li')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                if u"Buy" == product.xpath('.//a[@class="coll-prod-buy styled-small-button"]/text()')[0].extract().strip():
                    product_page_url = u"http://www.u-care.com.au"+product.xpath('.//a[@class="coll-prod-title"]/@href')[0].extract()
                    logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                    #yield Request(product_page_url,callback = self.parse_page,dont_filter=True)
                    yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%product.xpath('.//a[@class="coll-prod-title"]/@href')[0].extract())

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//h1[@itemprop="name"]/text()')[0].extract()
        try:
            item['info'] = sel.xpath('//div[@id="full_description"]')[0].extract()
        except:
            item['info'] = ''
        try:
            item['category'] = 'u-care'
        except:
            item['category'] = ''
        item['domain'] = 'www.u-care.com.au'
        try:
            item['brand'] = 'U-Care'
        except:
            item['brand'] = item['name'].split()[0]
        try:
            price = sel.xpath('//span[@class="product-price"]/text()')[0].extract()[1:]
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = '0'
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'AUD'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        image = "http:" + sel.xpath('//div[@id="product-photo-container"]/a/img/@src')[0].extract()
        item['image_urls'].append(image)
        pictures.append({'sml':image,'lrg':image,'zoom':image})


        # for thumb in sel.xpath('//ul[@id="thumbs_list_frame"]/li'):
        #     if not thumb.xpath('.//div[@class="quick_videop"]').extract():
        #         if thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default') not in item['image_urls']:
        #             item['image_urls'].append(thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default'))
        #             pictures.append({'sml':thumb.xpath('.//img/@src')[0].extract(),'lrg':thumb.xpath('.//img/@src')[0].extract().replace('cart_default','large_default'),'zoom':thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default')})
        item['pictures'] = json.dumps(pictures)
        if not item['pictures']:
            logging.log(logging.WARNING, "This product pictures is null: %s"%item['url'])
        item['targetId'] = 'www.u-care.com.au' + sel.xpath('//select[@id="product-select"]/option/@value')[0].extract()

        convert_kg = lambda x: '{}'.format(x/1000 + 0.3)
        weightlist = re.findall(u'(?i)([\d]+)[\s]?[g|克]',item['name'])
        if not weightlist:
            weightlist = re.findall(u'(?i)([\d]+)[\s]?[g|克]',item['info'])
        try:
            weight = convert_kg(float(weightlist[0]))
        except:
            weight = 0
        item['weight'] = weight
        logging.log(logging.WARNING, "This product %s weight is : %s"%(item['url'],item['weight']))

        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        return item
