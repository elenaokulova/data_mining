import scrapy
import pymongo
import os
from urllib.parse import unquote
import requests
import re


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    url_api = 'https://api.youla.io/api/v1/'

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient(os.getenv('DATA_BASE'))['parse_gb_11'][self.name]

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,
            'autor': self.get_user(self.get_product_id(response)),
            'specification': self.get_specs(response.css('.AdvertSpecs_row__ljPcX')),
        }
        self.db.insert_one(data)

    @staticmethod
    def get_specs(specs_html: scrapy.Selector):
        specs = []
        for spec in specs_html:
            s = {}
            spec_name = spec.css('.AdvertSpecs_label__2JHnS::text').get()
            spec_value = spec.css('.AdvertSpecs_data__xK2Qx::text').get()
            if not spec_value:
                spec_value = spec.css('.AdvertSpecs_data__xK2Qx a::text').get()
            s[spec_name] = spec_value
            specs.append(s.copy())
        return specs

    @staticmethod
    def get_product_id(response):
        content = unquote(str(response._get_body()))
        youla_id = re.search(r'"youlaId","[\da-zA-Z]*"', content)[0].split(',')[1]
        youla_id = youla_id[1:-1]
        return youla_id

    @staticmethod
    def get_user(product_id: str):
        url_api = 'https://api.youla.io/api/v1/product/'
        url_api_product = url_api + product_id
        info_product = requests.get(url_api_product).json()
        user_url = 'https://youla.ru/user/'
        user_id = info_product['data']['owner']['id']
        user_url += user_id
        return user_url
