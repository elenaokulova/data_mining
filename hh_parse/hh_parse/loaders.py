from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
import unicodedata
from urllib.parse import urljoin, unquote
from .items import HhVacParseItem, HhAuthorParseItem


def price_out(data: list):
    result = ''
    diapazon = None
    for itm in data:
        if itm == ' до ':
            diapazon = True
        if itm in [' до вычета налогов', ' на руки']:
            continue
        result += unicodedata.normalize("NFKD", itm)
    return result[3:] if not diapazon else result


def title_in(data: list):
    result = ''
    for itm in data:
        if itm == ' ':
            continue
        result += unicodedata.normalize("NFKD", itm)
    return result.strip()

def spheres_out(data: list):
    return data[0].lower().split(', ')

def author_url_out(data: list):
    return urljoin(data[0], data[1])


class HhVacLoader(ItemLoader):
    default_item_class = HhVacParseItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    author_url_out = author_url_out
    description_in = Join()
    description_out = TakeFirst()
    price_out = price_out


class HhAuthorLoader(ItemLoader):
    default_item_class = HhAuthorParseItem
    url_out = TakeFirst()
    title_in = title_in
    title_out = TakeFirst()
    site_out = TakeFirst()
    spheres_out = spheres_out
    description_in = Join()
    description_out = TakeFirst()
