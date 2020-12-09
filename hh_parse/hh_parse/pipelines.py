# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class HhParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_hh']

    def process_item(self, item, spider):
        if 'author_url' in item:
            name_collection = 'vacancy'
        else:
            name_collection = 'company'
        collection = self.db[name_collection]
        collection.insert_one(item)
        return item