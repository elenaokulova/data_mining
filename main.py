import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.instagram import InstagramSpider
from gb_parse.spiders.instagram_post import InstagramPostSpider

import dotenv

# from gb_parse import settings
dotenv.load_dotenv('.env')
tag_list = ['python', 'pythonlearning', 'pythonprogrammer', ]
accounts_list = ['rafaelmedioni', 'den_ananda', 'zuricaatassss', 'rolitas_basics', 'karenswiftie_13', ]

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramPostSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'), accounts_list=accounts_list)
    #crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'), password=os.getenv('PASSWORD'), tag_list=tag_list)
    crawl_proc.start()
