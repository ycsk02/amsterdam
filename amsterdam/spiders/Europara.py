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

class EuroparaSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #     }
    # }
    name = "Europara"
    allowed_domains = ["europara.cn"]

    # def get_starturls():
    #     response_page = requests.get('http://www.kiddies-kingdom.com/')
    #     sel_page = Selector(response_page)
    #     categorylink = sel_page.xpath('//a[contains(@class,"menulinks_mm ma_level_2")]/@href').extract()
    #     return categorylink
    #
    # start_urls = get_starturls()
    start_urls = ['https://www.europara.cn/44-%E5%A5%B6%E7%B2%89%E7%B3%BB%E5%88%97',]

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//li[@class="pagination_next"]//a',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//ul[@class="product_list grid row"]/li')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                if u"加入购物车" == product.xpath('.//a[@class="button ajax_add_to_cart_button btn btn-default"]/@title')[0].extract():
                    product_page_url = product.xpath('.//h5/a/@href')[0].extract()
                    logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                    #yield Request(product_page_url,callback = self.parse_page,dont_filter=True)
                    yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%product.xpath('.//h5/a/@href')[0].extract())

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//h1[@itemprop="name"]/text()')[0].extract()
        try:
            item['info'] = sel.xpath('//div[@id="short_description_content"]')[0].extract()
        except:
            item['info'] = ''
        try:
            item['category'] = ",".join(sel.xpath('//span[@itemprop="title"]/text()').extract())
        except:
            item['category'] = ''
        item['domain'] = 'www.europara.cn'
        try:
            item['brand'] = sel.xpath('//span[@itemprop="name"]/text()')[0].extract()
        except:
            item['brand'] = item['name'].split()[0]
        try:
            price = sel.xpath('//span[@id="our_price_display"]/text()')[0].extract()
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract()
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'EUR'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []

        for thumb in sel.xpath('//ul[@id="thumbs_list_frame"]/li'):
            if not thumb.xpath('.//div[@class="quick_videop"]').extract():
                if thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default') not in item['image_urls']:
                    item['image_urls'].append(thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default'))
                    pictures.append({'sml':thumb.xpath('.//img/@src')[0].extract(),'lrg':thumb.xpath('.//img/@src')[0].extract().replace('cart_default','large_default'),'zoom':thumb.xpath('.//img/@src')[0].extract().replace('cart_default','thickbox_default')})
        item['pictures'] = json.dumps(pictures)
        if not item['pictures']:
            logging.log(logging.WARNING, "This product pictures is null: %s"%item['url'])
        item['targetId'] = 'www.europara.cn' + sel.xpath('//input[@id="product_page_product_id"]/@value')[0].extract()
        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        item['weight'] = 0
        return item
