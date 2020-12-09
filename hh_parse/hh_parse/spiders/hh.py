import scrapy
from urllib.parse import urljoin
from ..loaders import HhVacLoader, HhAuthorLoader


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    selectors = {
        'url_vac': '//a[contains(@data-qa,"vacancy-title")]/@href',
        'pag_pages': '//a[contains(@class,"HH-Pager-Control")]/@href',
        'vac_author': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
    }

    vacancy = {
        'title': '//h1/text()',
        'price': '//p[@class="vacancy-salary"]/span/text()',
        'description': '//div[@data-qa="vacancy-description"]//*/text()',
        'skills': '//span[@data-qa = "bloko-tag__text"]/text()',
        'author_url': '//a[@data-qa = "vacancy-company-name"]/@href'
    }
    author_page = {
        'title': '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        'site': '//a[@data-qa="sidebar-company-site"]/@href',
        'spheres':'//div[text()="Сферы деятельности"]/../p/text()',
        'description': '//div[@class="g-user-content"]//*/text()'
    }

    def parse(self, response):
        for pag_page in response.xpath(self.selectors['pag_pages']):
            yield response.follow(urljoin(response.url, pag_page.get()), callback=self.parse)

        for vac_page in response.xpath(self.selectors['url_vac']):
            yield response.follow(vac_page.get(), callback=self.vac_parse)

    def vac_parse(self, response):
        for author_page in response.xpath(self.vacancy['author_url']):
            yield response.follow(urljoin(response.url, author_page.get()), callback=self.author_parse)

        loader = HhVacLoader(response=response)
        loader.add_value('url', response.url)
        loader.add_value('author_url', response.url)
        for name, selector in self.vacancy.items():
            loader.add_xpath(name, selector)

        yield loader.load_item()

    def author_parse(self, response):
        for vac_page in response.xpath(self.selectors['vac_author']):
            yield response.follow(vac_page.get(), callback=self.vac_parse)

        loader = HhAuthorLoader(response=response)
        test = response.xpath('//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()')
        loader.add_value('url', response.url)
        for name, selector in self.author_page.items():
            loader.add_xpath(name, selector)

        yield loader.load_item()

