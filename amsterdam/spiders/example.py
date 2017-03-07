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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ExampleSpider(CrawlSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            # 'amsterdam.pipelines.MyImagePipeline': 200,
            # 'amsterdam.pipelines.AddTablePipeline': 400,
            # 'amsterdam.pipelines.AddElasticsearchPipeline':900,
            # 'amsterdam.pipelines.UpdatePricePipeline':1200,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'amsterdam.middlewares.random_useragent.RandomUserAgentMiddleware': None,
            'amsterdam.middlewares.JSMiddleware.Example_JSMiddleware': 420,
        }
    }
    name = "example"
    allowed_domains = ["example.com",]

    start_urls = ['http://www.example.com',]

    def parse(self,response):
        driver = response.meta['driver']
        n = 0
        while n < 3:
            try:
                sel = Selector(text=driver.page_source)
                for p in sel.xpath('//div[@class="table"]/ul/li'):
                    print p.xpath('.//span[@class="li03"]/a/text()')[0].extract()

                next_btn = WebDriverWait(driver, 20).until(
                     EC.visibility_of_element_located((By.LINK_TEXT, u"下一页"))
                        )
                next_btn.click()
                n += 1
            except:
                break
