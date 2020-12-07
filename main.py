from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from hw4_parse.spiders.autoyoula import AutoyoulaSpider

# from gb_parse import settings

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('hw4_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(AutoyoulaSpider)
    crawl_proc.start()
