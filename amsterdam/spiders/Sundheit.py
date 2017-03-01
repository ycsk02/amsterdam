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

class SundheitSpider(CrawlSpider):
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #         # 'amsterdam.pipelines.MyImagePipeline': 200,
    #         # 'amsterdam.pipelines.AddTablePipeline': 400,
    #         # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
    #         # 'amsterdam.pipelines.UpdatePricePipeline':1200,
    #     }
    # }
    name = "Sundheit"
    allowed_domains = ["sundheit.de"]

    start_urls = ['https://sundheit.de/pl/express.html',]

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//a[@class="next i-next"]',)),
                           callback='parse_start_url',
                           follow=True
        ),
    )


    def parse_start_url(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//ul[@class="products-grid  columns4"]/li')
        for product in product_list:
            #判断商品是否下架,只处理上架商品
            try:
                if u"添加到购物车" == product.xpath('.//a[@class="addtocart"]/span/text()')[0].extract().strip():
                    product_page_url = product.xpath('.//h2/a/@href')[0].extract()
                    logging.log(logging.WARNING, "We created a new product url: %s"%product_page_url)
                    #yield Request(product_page_url,callback = self.parse_page,dont_filter=True)
                    yield Request(product_page_url,callback = self.parse_page)
            except:
                logging.log(logging.WARNING, "This product is not available: %s"%product.xpath('.//h2/a/@href')[0].extract())

    def parse_page(self,response):
        sel = Selector(response)
        item = ProductItem()
        item['url'] = response.url
        logging.log(logging.WARNING, "I get this product in page: %s"%item['url'])
        item['name'] = sel.xpath('//div[@class="product-name"]/h1/text()')[0].extract()
        try:
            item['info'] = sel.xpath('//div[@id="tab_description_tabbed_contents"]')[0].extract()
        except:
            item['info'] = ''
        try:
            item['category'] = ''
        except:
            item['category'] = ''
        item['domain'] = 'sundheit.de'
        brands = ['Holle','Hipp']
        try:
            item['brand'] = [x for x in brands if x.lower() in item['name'].lower()][0]
        except:
            item['brand'] = ''
        try:
            price = sel.xpath('//span[@class="price"]/text()')[0].extract()[:-1].strip()
            item['price'] = Decimal(price)
        except:
            item['price'] = '0'
        try:
            #oldprice = sel.xpath('//span[@id="old_price_display"]/text()')[0].extract().split()[1]
            oldprice = '0'
            item['oldprice'] = Decimal(oldprice)
        except:
            item['oldprice'] = '0'
        item['currency'] = 'EUR'
        item['createdTime'] = int(time.time())
        item['lastUpdatedTime'] = int(time.time())
        pictures = []
        item['image_urls'] = []
        image = sel.xpath('//img[@class="etalage_thumb_image"]/@src')[0].extract()
        item['image_urls'].append(image)
        pictures.append({'sml':image,'lrg':image,'zoom':image})

        item['pictures'] = json.dumps(pictures)
        if not item['pictures']:
            logging.log(logging.WARNING, "This product pictures is null: %s"%item['url'])
        item['targetId'] = 'sundheit.de' + sel.xpath('//form[@id="product_addtocart_form"]/div/input[@name="product"]/@value')[0].extract()

        convert_kg = lambda x: '{}'.format(x/1000 + 0.3)
        weightlist = re.findall(u'(?i)([\d]+)[\s]?[g|克]',item['name'])
        weight = convert_kg(float(weightlist[0]))
        item['weight'] = weight
        logging.log(logging.WARNING, "This product %s weight is : %s"%(item['url'],item['weight']))
        #以下未取到数据
        item['size'] = ''
        item['color'] = ''
        item['mainPicture'] = ''
        item['lpictures'] = ''
        return item
