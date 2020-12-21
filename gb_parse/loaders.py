import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from .items import AutoYoulaItem, HHVacancyItem, InstagramPostItem, InstagramTagItem, TagInfoItem, PostInfoItem


def get_autor(js_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, js_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


def get_specifications(itm):
    tag = Selector(text=itm)
    result = {tag.css('.AdvertSpecs_label__2JHnS::text').get(): tag.css(
        '.AdvertSpecs_data__xK2Qx::text').get() or tag.css('a::text').get()}
    return result


def specifications_out(data: list):
    result = {}
    for itm in data:
        result.update(itm)
    return result


class AutoYoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_out = TakeFirst()
    autor_in = MapCompose(get_autor)
    autor_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = specifications_out


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()


class InstagramTagLoader(ItemLoader):
    default_item_class = InstagramTagItem
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class TagLoader(ItemLoader):
    default_item_class = TagInfoItem
    id_insta_out = TakeFirst()
    url_out = TakeFirst()
    name_out = TakeFirst()
    profile_pic_url_out = TakeFirst()
    count_media_out = TakeFirst()


class InstagramPostLoader(ItemLoader):
    default_item_class = InstagramPostItem
    date_parse_out = TakeFirst()
    data_out = TakeFirst()

class PostLoader(ItemLoader):
    default_item_class = PostInfoItem
    post_id_out = TakeFirst()
    text_in = Join()
    text_out = TakeFirst()
    shortcode_out = TakeFirst()
    likes_out = TakeFirst()
    owner_id_out = TakeFirst()
    is_video_out = TakeFirst()
    accessibility_caption_out = TakeFirst()
    image_out = TakeFirst()