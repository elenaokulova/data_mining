# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_gb_11_3']

    def process_item(self, item, spider):
        #if spider.db_type == 'MONGO':
        collection = self.db[spider.name]
        collection.insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if 'image' in item['data']:
            img_url = item['data'].get('image', [])
            yield Request(img_url)

    def item_completed(self, results, item, info):
        if 'image' in item['data']:
            item['data']['image'] = results[0][1]
        return item
