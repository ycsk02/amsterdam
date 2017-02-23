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

class KiddiesKingdomSpider(CrawlSpider):
    name = "KiddiesKingdom"
    allowed_domains = ["kiddies-kingdom.com","netdna-ssl.com"]

    def get_starturls():
        response_page = requests.get('http://www.kiddies-kingdom.com/')
        sel_page = Selector(response_page)
        categorylink = sel_page.xpath('//a[contains(@class,"menulinks_mm ma_level_2")]/@href')[0:39].extract()
        return categorylink

    start_urls = get_starturls()
    #start_urls = ['http://www.kiddies-kingdom.com/96-doorway-bouncers',]

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//li[@class="pagination_next"]//a',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//ul[@id="product_list"]/li')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                if "Add to Basket" == product.xpath('.//a[@class="ajax_add_to_cart_button exclusive blue "]/text()')[0].extract():
                    product_page_url = product.xpath('.//h3/a/@href')[0].extract()
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
        item['name'] = sel.xpath('//div[@itemprop="name"]/text()')[0].extract()
        item['info'] = sel.xpath('//div[@itemprop="description"]')[0].extract()
        try:
            item['category'] = " ".join(sel.xpath('//div[@class="topbreadhead"]/text()').extract())
        except:
            item['category'] = ''
        item['domain'] = 'www.kiddies-kingdom.com'
        item['brand'] = item['name'].split()[0]
        try:
            price = sel.xpath('//span[@id="our_price_display"]/text()')[0].extract()[1:]
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract()[1:]
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'GBP'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        for thumb in sel.xpath('//ul[@id="thumbs_list_frame"]/li'):
            item['image_urls'].append(thumb.xpath('.//img/@src')[0].extract().replace('small_default','thickbox_default'))
            pictures.append({'sml':thumb.xpath('.//img/@src')[0].extract(),'lrg':thumb.xpath('.//img/@src')[0].extract().replace('small_default','large_default'),'zoom':thumb.xpath('.//img/@src')[0].extract().replace('small_default','thickbox_default')})
        item['pictures'] = json.dumps(pictures)
        item['targetId'] = 'www.kiddies-kingdom.com' + sel.xpath('//input[@id="product_page_product_id"]/@value')[0].extract()
        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        return item
