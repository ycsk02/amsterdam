# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.selector import Selector
from re import sub
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from decimal import Decimal
from amsterdam.items import ProductItem
import requests

class KiddiesKingdomSpider(CrawlSpider):
    custom_settings = {
        'IMAGES_STORE':'/images',
        'LOG_LEVEL':'ERROR',
        'ITEM_PIPELINES': {
            'pipelines.AddTablePipeline': 400,
            'scrapy.pipelines.images.ImagesPipeline': 1,
        }
    }
    name = "KiddiesKingdom"
    allowed_domains = ["www.kiddies-kingdom.com","kkcdn-kiddieskingdom.netdna-ssl.com"]

#    start_urls = ["http://www.kiddies-kingdom.com/51-0-13kg-0-12mths-group-0",
#        "http://www.kiddies-kingdom.com/295-bath-tubs-sets",
#        "http://www.kiddies-kingdom.com/71-bouncers-rockers",
#        "http://www.kiddies-kingdom.com/25-travel-systems",
#    ]
#file://127.0.0.1/path/to/file.html
#with open('products.json','r') as jsonfile:
#   jsondata = json.load(jsonfile)
#for p in jsondata["products"]:
#     print p["id"]
# '''
# headers = {
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Encoding': 'gzip, deflate, sdch',
#             'Accept-Language': 'en-GB,en-US;q=0.8,en;q=0.6',
#             'Connection': 'keep-alive',
#             'Upgrade-Insecure-Requests': '1',
#             'Proxy-Connection': 'keep-alive',
#             'Pragma': 'no-cache',
#             'Cache-Control': 'no-cache',
#             'Host': 'images.finishline.com',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
#         }
# '''
    def get_starturls():
        response_page = requests.get('http://www.kiddies-kingdom.com/')
        sel_page = Selector(response_page)
        return sel_page.xpath('//a[contains(@class,"menulinks_mm ma_level_2")]/@href').extract()

    start_urls = get_starturls()

    rules = (
        Rule(LinkExtractor(allow=(),restrict_xpaths=('//li[@class="pagination_next"]//a',)),
                           callback='parse_items',
                           follow=True
        ),
    )

    def parse_items(self, response):
        sel = Selector(response)
        product_list = sel.xpath('//ul[@id="product_list"]/li')
        items = []
        for product in product_list:
            item = ProductItem()
            item['name'] = product.xpath('.//h3/a/text()')[0].extract()
            item['domain'] = 'www.kiddies-kingdom.com'
            item['brand'] = product.xpath('.//h3/a/text()')[0].extract().split()[0]
            try:
                price = product.xpath('.//span[@class="price"]/text()')[0].extract()
                item['price'] = Decimal(sub(r'[^\d.]','',price))
            except:
                item['price'] = '0'
            try:
                oldprice = product.xpath('.//span[@class="rrp_price_cat"]/text()')[0].extract()
                item['oldprice'] = Decimal(sub(r'[^\d.]','',oldprice))
            except:
                item['oldprice'] = 0
            item['currency'] = 'GBP'
            item['url'] = product.xpath('.//h3/a/@href')[0].extract()
            item['createdTime'] = int(time.time())
            item['lastUpdatedTime'] = int(time.time())
            item['mainPicture'] = product.xpath('.//div[@class="imagelistblock"]/a/img/@src')[0].extract()
            item['image_urls'] = [item['mainPicture']]
            items.append(item)
        return items
