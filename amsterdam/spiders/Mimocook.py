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

class MimocookSpider(CrawlSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            'amsterdam.pipelines.MyImagePipeline': None,
            'amsterdam.pipelines.AddTablePipeline': 400,
            'amsterdam.pipelines.AddElasticsearchPipeline':900,
            'amsterdam.pipelines.UpdatePricePipeline':1200,
        }
    }
    name = "Mimocook"
    allowed_domains = ["mimocook.com"]

    def get_starturls():
        response_page = requests.get('http://www.mimocook.com/en/')
        sel_page = Selector(response_page)
        categorylink = sel_page.xpath('//div[@class="cbp-category-link-w"]/a/@href').extract()
        categorylink.append('http://www.mimocook.com/en/sales')
        return categorylink

    start_urls = get_starturls()
    #start_urls = ['http://www.mimocook.com/en/kitchen-scales-111',]

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
                if "Available" == product.xpath('.//span[@class="availabile_product"]/text()')[0].extract():
                    product_page_url = product.xpath('.//a[@class="product-name"]/@href')[0].extract()
                    logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                    #yield Request(product_page_url,callback = self.parse_page,dont_filter=True)
                    yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%response.url)

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//h1[@itemprop="name"]/text()')[0].extract()
        item['info'] = sel.xpath('//div[@class="product-tabs-container"]')[0].extract()
        try:
            item['category'] = " ".join(sel.xpath('//span[@itemprop="title"]/text()').extract())
        except:
            item['category'] = ''
        item['domain'] = 'www.mimocook.com'
        item['brand'] = sel.xpath('//span[@itemprop="brand"]/text()')[0].extract()
        try:
            price = sel.xpath('//span[@id="our_price_display"]/text()')[0].extract().split()[1]
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = sel.xpath('//span[@id="old_price_display"]/span[@class="price"]/text()')[0].extract().split()[1]
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'EUR'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        for thumb in sel.xpath('//ul[@id="thumbs_list_frame"]/li'):
            item['image_urls'].append(thumb.xpath('.//img/@src')[0].extract().replace('small_default','thickbox_default'))
            pictures.append({'sml':thumb.xpath('.//img/@src')[0].extract(),'lrg':thumb.xpath('.//img/@src')[0].extract().replace('small_default','large_default'),'zoom':thumb.xpath('.//img/@src')[0].extract().replace('small_default','thickbox_default')})
        item['pictures'] = json.dumps(pictures)
        item['targetId'] = 'www.mimocook.com' + sel.xpath('//span[@itemprop="sku"]/@content')[0].extract()
        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        return item
