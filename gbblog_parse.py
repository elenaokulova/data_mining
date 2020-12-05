from typing import Tuple, Set
import bs4
import requests
from urllib.parse import urljoin
from database import GBDataBase
from datetime import datetime


class GbBlogParse:

    def __init__(self, start_url):
        self.start_url = start_url
        self.comments = []
        self.page_done = set()
        self.db = GBDataBase('sqlite:///gb_blog.db')

    # добавили возможность возврата json для комментариев
    def _get(self, url, params='', json=False):
        response = requests.get(url, params)
        # todo Обработка статусов и ошибки
        self.page_done.add(url)
        if not json:
            return bs4.BeautifulSoup(response.text, 'lxml')
        else:
            return response.json()

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self._get(url)
            posts, pagination = self.parse(soup)
            for post_url in posts:
                page_data = self.page_parse(self._get(post_url), post_url)
                self.save(page_data)

            for pag_url in pagination:
                self.run(pag_url)

    def parse(self, soup) -> Tuple[Set[str], Set[str]]:
        pag_ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, p_url.get('href')) for p_url in pag_ul.find_all('a') if p_url.get('href')
        )
        posts_wrapper = soup.find('div', attrs={'class': 'post-items-wrapper'})

        posts = set(
            urljoin(self.start_url, post_url.get('href')) for post_url in
            posts_wrapper.find_all('a', attrs={'class': 'post-item__title'})
        )

        return posts, paginations

    def page_parse(self, soup, url) -> dict:
        return {
            'post_data': {
                'url': url,
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'image': soup.find('div', attrs={'class': 'blogpost-content'}).find('img').get('src') if soup.find(
                    'div', attrs={'class': 'blogpost-content'}).find('img') else None,
                'date': datetime.strptime(soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').get('datetime'),"%Y-%m-%dT%H:%M:%S%z"),
            },
            'writer': {
                'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                'url': urljoin(self.start_url, soup.find('div', attrs={'itemprop': 'author'}).parent.get('href'))
            },
            'comments': [comment for comment in self._get_comments(soup)],
            'tags': [tag for tag in self._get_tags(soup)]
        }

    def _get_comments(self, soup):
        comments_id = soup.find('comments').attrs['commentable-id']
        params = {
            'commentable_type': 'Post',
            'commentable_id': comments_id
        }
        comments_json = self._get(url='https://geekbrains.ru/api/v2/comments', params=params, json=True)
        self.comments = []
        self.comm_parse(comments_json)
        return self.comments

    def comm_parse(self, json):
        comment = {}
        for com in json:
            comment['text'] = com['comment']['body']
            comment['author'] = com['comment']['user']['first_name']
            self.comments.append(comment.copy())
            if com['comment']['children']:
                self.comm_parse(com['comment']['children'])

    def _get_tags(self, soup):
        tags_soup = soup.find_all('a', attrs={'class': 'small'})
        for tag in tags_soup:
            yield {'url': urljoin(self.start_url, tag.get('href')), 'name': tag.text}

    def save(self, post_data: dict):
        self.db.create_post(post_data)


if __name__ == '__main__':
    parser = GbBlogParse('https://geekbrains.ru/posts')
    parser.run()
