import json
import scrapy
from ..loaders import InstagramPostLoader, InstagramTagLoader, TagLoader, PostLoader
import datetime
from urllib.parse import urlencode


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']

    query_hash = {
        'tag_paginate': '9b498c08113f1e09617a1703c22b2f32'
    }
    variables = {"tag_name": "python",
                 "first": 100,
                 "after": "QVFEeGhna1dpcnZuQUFfbDQ2eGV1SzZUVWtVMDBuTGc1UnZJVkw4WW1EakpvTF8xVXlJQWRYWXhWVHdBX0hqYWkzLXE3b3BDNVRnbTVpWEVnN0QzSDEtUA=="}

    def __init__(self, login, password, tag_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.tag_list = tag_list
        super(InstagramSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError:
            if response.json().get('authenticated'):
                for tag in self.tag_list:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)
        print(1)

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        data_tag = js_data['entry_data']['TagPage'][0]['graphql']['hashtag']
        tag_info = {
            'id_insta': data_tag['id'],
            'url': response.url,
            'name': data_tag['name'],
            'profile_pic_url': data_tag['profile_pic_url'],
            'count_media': data_tag['edge_hashtag_to_media']['count'],
        }
        loader = InstagramTagLoader(response=response)
        loader.add_value('date_parse', datetime.datetime.now())
        loader_tag = TagLoader(response=response)
        for key, value in tag_info.items():
            loader_tag.add_value(key, value)
        loader.add_value('data', dict(loader_tag.load_item()))
        yield loader.load_item()

        next_page = data_tag['edge_hashtag_to_media']['page_info']['has_next_page']
        if next_page:
            self.variables['after'] = data_tag['edge_hashtag_to_media']['page_info']['end_cursor']
            self.variables['tag_name'] = tag_info['name']
            params = {
                'query_hash': self.query_hash['tag_paginate'],
                'variables': json.dumps(self.variables)
            }
            url_api = f'https://www.instagram.com/graphql/query/?{urlencode(params)}'
            yield response.follow(url_api, callback=self.tag_parse_api)

    def tag_parse_api(self, response):
        data = json.loads(response.body)
        for post in data['data']['hashtag']['edge_hashtag_to_media']['edges']:
            data_post = self.data_post(post['node'])
            loader = InstagramPostLoader()
            loader.add_value('date_parse', datetime.datetime.now())
            loader_post = PostLoader()
            for key, info in data_post.items():
                loader_post.add_value(key, info)
            loader.add_value('data', dict(loader_post.load_item()))
            yield loader.load_item()

        next_page = data['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        if next_page:
            self.variables['after'] = data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            self.variables['tag_name'] = data['data']['hashtag']['name']
            params = {
                'query_hash': self.query_hash['tag_paginate'],
                'variables': json.dumps(self.variables)
            }
            url_api = f'https://www.instagram.com/graphql/query/?{urlencode(params)}'
            yield response.follow(url_api, callback=self.tag_parse_api)

    def data_post(self, post):
        data = {
            'post_id': post['id'],
            'text': post['edge_media_to_caption']['edges'][0]['node']['text'],
            'shortcode': post['shortcode'],
            'likes': post['edge_liked_by']['count'],
            'owner_id': post['owner']['id'],
            'is_video': post['is_video'],
            'accessibility_caption': post['accessibility_caption'],
            'image': post['thumbnail_resources'][-1]['src']
        }
        return data


    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])
