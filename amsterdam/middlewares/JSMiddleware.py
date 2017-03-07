# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse
from scrapy import signals
from scrapy.utils.python import to_bytes
import time

class Example_JSMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        request.meta['driver'] = self.driver  # to access driver from response
        self.driver.get(request.url)
        time.sleep(1)
        body = to_bytes(self.driver.page_source)  # body must be of type bytes
        return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)

    def spider_opened(self, spider):
        self.driver = webdriver.PhantomJS()

    def spider_closed(self, spider):
        self.driver.close()
