# -*- coding: utf-8 -*-
from amsterdam.spiders.Mimocook import MimocookSpider
from amsterdam.spiders.Skinstore import SkinstoreSpider
from amsterdam.spiders.Byboj import BybojSpider

import scrapy
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
import logging

configure_logging({'LOG_LEVEL':'INFO','LOG_FILE':'CrawlSpider.log',
    'LOG_FORMAT':'%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    'LOG_DATEFORMAT':'%Y-%m-%d %H:%M:%S',
    })

settings = get_project_settings()
runner = CrawlerRunner(settings)

runner.crawl(MimocookSpider)
#runner.crawl(SkinstoreSpider)
#runner.crawl(BybojSpider)

d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()
