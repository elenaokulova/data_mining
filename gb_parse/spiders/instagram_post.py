import scrapy
import json
from urllib.parse import urlencode, parse_qs
import datetime as dt
from ..items import InstaPost


class InstagramPostSpider(scrapy.Spider):
    name = 'instagram_post'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']

    query_hash = {
        'followers': 'c76146de99bb02f6415203be841dd25a',
        'following': 'd04b0a864b4b54837c0d870b0e77e076'
    }

    url_api = 'https://www.instagram.com/graphql/query/'
    variables = {"id": '',
                 'include_reel': 'true',
                 'fetch_mutual': 'false',
                 'first': 100,
                 'after': ''
                 }
    db_follow = {}

    def __init__(self, login, password, accounts_list, *args, **kwargs):
        self.login = login
        self.password = password
        self.accounts_list = accounts_list
        super(InstagramPostSpider, self).__init__(*args, **kwargs)

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
                for account in self.accounts_list:
                    yield response.follow(f'/{account}/', callback=self.acc_parse)
        print(1)

    def acc_parse(self, response):
        js_data = self.js_data_extract(response)
        js_data_user = js_data['entry_data']['ProfilePage'][0]['graphql']['user']
        username = js_data_user['username']

        is_private = js_data_user['is_private']
        self.variables['id'] = js_data_user['id']
        params_followers = {
            'query_hash': self.query_hash['followers'],
            'variables': json.dumps(self.variables)
        }

        data_user = {
            'date_parse': dt.datetime.utcnow(),
            'name': username,
            'id_insta': js_data_user['id'],
            'followers': [],
            'following': []
        }
        self.db_follow[data_user['id_insta']] = data_user

        if not is_private:
            yield from self.parse_api(params_followers, response)

    def post_api_parse(self, response):
        yield from self.parse_api(response.json()['data']['user']['edge_followed_by']['page_info']['end_cursor'],
                                  response)

    def parse_api(self, params, response):
        foll = []
        try:
            data = json.loads(response.body)
            next_url = parse_qs(response.url)
            local_var = self.variables.copy()
            local_var['id'] = next_url['variables'][0].split('"')[3]
            if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                after = data['data']['user']['edge_followed_by']['page_info']['end_cursor']
                local_var['after'] = after
                params = {
                    'query_hash': self.query_hash['followers'],
                    'variables': json.dumps(local_var)
                }
                url_api = f'{self.url_api}?{urlencode(params)}'

                yield response.follow(
                    url_api,
                    callback=self.post_api_parse)

            for pack_follow in self.parse_followers(data):
                self.db_follow[local_var['id']]['followers'].append(pack_follow)

            yield InstaPost(
                date_parse=self.db_follow[local_var['id']]['date_parse'],
                name=self.db_follow[local_var['id']]['name'],
                id_insta=self.db_follow[local_var['id']]['id_insta'],
                followers=self.db_follow[local_var['id']]['followers']
            )

        except ValueError:
            url = f'{self.url_api}?{urlencode(params)}'
            yield response.follow(
                url,
                callback=self.post_api_parse)

    @staticmethod
    def parse_followers(data):
        for user in data['data']['user']['edge_followed_by']['edges']:
            yield user['node']['username']

    def js_data_extract(self, response):
        script = response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get()
        return json.loads(script.replace("window._sharedData = ", '')[:-1])
