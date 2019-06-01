import scrapy
from scrapy import cmdline
import requests
import json
from lxml import html
import pandas as pd
import time
from bs4 import BeautifulSoup
import sys, os
import optparse
import cProfile
import inspect
import pkg_resources

import scrapy
from scrapy.cmdline import *
from scrapy.crawler import CrawlerProcess
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError
from scrapy.utils.misc import walk_modules
from scrapy.utils.project import inside_project, get_project_settings
from scrapy.utils.python import garbage_collect
from scrapy.settings.deprecated import check_deprecated_settings


def execute(argv=None, settings=None):
    if argv is None:
        argv = sys.argv

    # --- backwards compatibility for scrapy.conf.settings singleton ---
    if settings is None and 'scrapy.conf' in sys.modules:
        from scrapy import conf
        if hasattr(conf, 'settings'):
            settings = conf.settings
    # ------------------------------------------------------------------

    if settings is None:
        settings = get_project_settings()
        # set EDITOR from environment if available
        try:
            editor = os.environ['EDITOR']
        except KeyError:
            pass
        else:
            settings['EDITOR'] = editor
    check_deprecated_settings(settings)

    # --- backwards compatibility for scrapy.conf.settings singleton ---
    import warnings
    from scrapy.exceptions import ScrapyDeprecationWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ScrapyDeprecationWarning)
        from scrapy import conf
        conf.settings = settings
    # ------------------------------------------------------------------

    inproject = inside_project()
    cmds = cmdline._get_commands_dict(settings, inproject)
    cmdname = cmdline._pop_command_name(argv)
    parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), conflict_handler='resolve')
    if not cmdname:
        cmdline._print_commands(settings, inproject)
        sys.exit(0)
    elif cmdname not in cmds:
        cmdline._print_unknown_command(settings, cmdname, inproject)
        sys.exit(2)

    cmd = cmds[cmdname]
    parser.usage = "scrapy %s %s" % (cmdname, cmd.syntax())
    parser.description = cmd.long_desc()
    settings.setdict(cmd.default_settings, priority='command')
    cmd.settings = settings
    cmd.add_options(parser)
    opts, args = parser.parse_args(args=argv[1:])
    cmdline._run_print_help(parser, cmd.process_options, args, opts)

    cmd.crawler_process = CrawlerProcess(settings)
    try:
        cmdline._run_print_help(parser, cmdline._run_command, cmd, args, opts)
    except Exception as e:
        print('Done')


class HaaretzCrawler(scrapy.Spider):
    name = "haaretz_spider"

    def start_requests(self):
        base_urls = [
            'https://www.haaretz.co.il/news/elections/',
            'https://www.haaretz.co.il/news/politi/'
        ]
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
        execute(
            ('scrapy runspider haaretz_spider.py -o %s.csv -t csv' % file_name).split())
        df = pd.read_csv('%s.csv' % file_name)
        df.to_excel('%s.xlsx' % file_name)


