# -*- coding: utf-8 -*-
# from spiders.KiddiesKingdom import KiddiesKingdomSpider
# from spiders.Amsterdam import AmsterdamSpider
from amsterdam.spiders.Mimocook import MimocookSpider
from amsterdam.spiders.Skinstore import SkinstoreSpider
from amsterdam.spiders.Byboj import BybojSpider

#from spiders.Amsterdam import AmsterdamSpider

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

# configure_logging(install_root_handler=False)
# logging.basicConfig(
#     filename='CrawlSpider.log',
#     format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
#     dateformat='%Y-%m-%d %H:%M:%S',
#     level=logging.INFO
# )

settings = get_project_settings()
runner = CrawlerRunner(settings)
#runner.crawl(KiddiesKingdomSpider)
runner.crawl(MimocookSpider)
#runner.crawl(SkinstoreSpider)
#runner.crawl(BybojSpider)
#runner.crawl(AmsterdamSpider)
d = runner.join()
d.addBoth(lambda _: reactor.stop())

reactor.run()
#    settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36")
