import scrapy
from scrapy import cmdline
import requests
import json
from lxml import html
import pandas as pd
import time
from bs4 import BeautifulSoup


class HaaretzCrawler(scrapy.Spider):
    name = "haaretz_spider"

    def start_requests(self):
        base_urls = ['https://www.haaretz.co.il/news/elections/', 'https://www.haaretz.co.il/news/politi/']
        for base_url in base_urls:
            api_url = 'https://www.haaretz.co.il/json/cmlink/7.3605536?vm=whtzResponsive&pidx={}&url={}&dataExtended=%7B%22contentId%22%3A%22%22%7D'
            api_request = api_url.format(str(1), base_url)
            response = requests.get(api_request).json()
            total_pages = response['pageCount']
            urls = [api_url.format(str(page), base_url) for page in range(1, total_pages + 1)]
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page_json = json.loads(response.text)
        articles = page_json.get('items', [])
        for item in articles:
            # parse_article = scrapy.Request(url=item.get('path'), callback=self.parse_article)
            article_html = requests.get(item.get('path'), timeout=(5, 14))
            soup = BeautifulSoup(article_html.content)
            # article_tree = html.fromstring(article_html.content)
            for i, paragraph in enumerate(soup.find('article').find_all('p', "t-body-text")):
                if paragraph.text:
                    # paragraph_body = html.fromstring(paragraph.text)
                    content = paragraph.text
                    parse_article = {
                        'id': item.get('id'),
                        'author': item.get('authors', [''])[0],
                        'title': item.get('title'),
                        'subTitle': item.get('subTitle'),
                        'path': item.get('path'),
                        'publishDate': item.get('publishDate'),
                        'paragraph': str(i + 1),
                        'content': content,
                    }
                    yield parse_article

    def parse_article(self, response):
        filter_fields = ['depth', 'download_timeout', 'download_slot', 'download_latency']

        # article_row['content'] = '<p>'.join(
        #     response.xpath('//article//div[@class="l-article__entry-wrapper"]//p[@class="t-body-text"]//text()').extract())
        for i, paragraph in enumerate(
                response.xpath('//article//div[@class="l-article__entry-wrapper"]//p[@class="t-body-text"]').extract()):
            article_row = {key: value for key, value in response.meta.items() if key not in filter_fields}
            article_row['paragraph'] = i
            article_row['content'] = str(paragraph.xpath('//text()').extract()).strip()
            yield article_row

    def extract_articles(self, file_name):
        cmdline.execute(
            ('scrapy runspider haaretz_spider.py -o %s.csv -t csv' % file_name).split())
        df = pd.read_csv('%s.csv' % file_name)
        df.to_excel('%s.xlsx' % file_name)
