import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
from urllib.parse import urljoin

dotenv.load_dotenv('.env')


class MagnitParse:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; rv:83.0) Gecko/20100101 Firefox/83.0'
    }

    month_list = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

    def __init__(self, start_url):
        self.start_url = start_url
        client = pymongo.MongoClient(os.getenv('DATA_BASE'))
        self.db = client['magnit']

        self.product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            'old_price': lambda soup: self.get_price(soup.find('div', attrs={'class': 'label__price_old'})),
            'new_price': lambda soup: self.get_price(soup.find('div', attrs={'class': 'label__price_new'})),
            'date_from': lambda soup: self.get_dates(soup.find('div', attrs={'class': 'card-sale__date'}))['date_from'],
            'date_to': lambda soup: self.get_dates(soup.find('div', attrs={'class': 'card-sale__date'}))['date_to'],

        }

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            pr_data = self.get_product(product)
            yield pr_data

    def get_product(self, product_soup) -> dict:

        result = {}
        for key, value in self.product_template.items():
            try:
                result[key] = value(product_soup)
            except Exception as e:
                continue
        return result

    # функция выцепления цены из фрагмента html
    def get_price(self, html) -> float:
        price_integer = html.find('span', attrs={'class': 'label__price-integer'}).text
        price_decimal = html.find('span', attrs={'class': 'label__price-decimal'}).text
        return int(price_integer) + int(price_decimal) / 100

    # функция получения дат из фрагмента html
    def get_dates(self, html: bs4.BeautifulSoup) -> dict:
        date_from_html = html.find_all('p')[0].text
        day_from = int(date_from_html.split()[1])
        mounth_from = self.month_list.index(date_from_html.split()[2].lower()) + 1
        year_from = dt.date.today().year
        date_from = dt.datetime(year_from, mounth_from, day_from)

        date_to_html = html.find_all('p')[1].text
        day_to = int(date_to_html.split()[1])
        mounth_to = self.month_list.index(date_to_html.split()[2].lower()) + 1
        year_to = dt.date.today().year + 1 if (mounth_to == 1) & (mounth_from == 12) else dt.date.today().year
        date_to = dt.datetime(year_to, mounth_to, day_to)

        return {'date_from': date_from, 'date_to': date_to}

    def save(self, product):
        collection = self.db['products']
        collection.insert_one(product)


if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()
