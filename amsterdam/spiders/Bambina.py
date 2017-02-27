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

class BambinaSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #     }
    # }
    name = "Bambina"
    allowed_domains = ["bambina.co.nz","shopify.com"]

    # def get_starturls():
    #     response_page = requests.get('http://www.kiddies-kingdom.com/')
    #     sel_page = Selector(response_page)
    #     categorylink = sel_page.xpath('//a[contains(@class,"menulinks_mm ma_level_2")]/@href').extract()
    #     return categorylink
    #
    # start_urls = get_starturls()
    start_urls = ['https://www.bambina.co.nz/collections/aptamil','https://www.bambina.co.nz/collections/karicare']

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//div[@class="pagination"]//a',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//div[@class="productlist"]/div')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                    product_page_url = u"https://www.bambina.co.nz"+product.xpath('.//div[@class="desc"]/a/@href')[0].extract()
                    logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                    yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%product.xpath('.//div[@class="desc"]/a/@href')[0].extract())

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//h1/text()')[0].extract()
        try:
            item['info'] = sel.xpath('//div[@class="description pagecontent simple"]')[0].extract()
        except:
            item['info'] = ''
        try:
            item['category'] = ''
        except:
            item['category'] = ''
        item['domain'] = 'www.bambina.co.nz'
        try:
            item['brand'] = 'bambina'
        except:
            item['brand'] = item['name'].split()[0]
        try:
            price = sel.xpath('//div[@id="price-field"]/text()')[0].extract().strip()[1:]
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = '0'
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'NZD'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        image = "http:" + sel.xpath('//div[@class="productimages"]/div/a/img/@src')[0].extract()
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
        item['targetId'] = 'www.bambina.co.nz' + sel.xpath('//form[@id="product-form"]/div/input[@name="id"]/@value')[0].extract()
        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        return item
