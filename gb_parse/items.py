# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Identity


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AutoYoulaItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    autor = scrapy.Field()
    specifications = scrapy.Field()


class HHVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    company_url = scrapy.Field()


class TagInfoItem(scrapy.Item):
    id_insta = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    count_media = scrapy.Field()


class InstagramTagItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field(input_processor=Identity())


class PostInfoItem(scrapy.Item):
    post_id = scrapy.Field()
    text = scrapy.Field()
    shortcode = scrapy.Field()
    likes = scrapy.Field()
    owner_id = scrapy.Field()
    is_video = scrapy.Field()
    accessibility_caption = scrapy.Field()
    image = scrapy.Field()


class InstagramPostItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field(input_processor=Identity())

class InstaPost(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    name = scrapy.Field()
    id_insta = scrapy.Field()
    followers = scrapy.Field()
    following = scrapy.Field()
