import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

class YnetCrawler:
    def __init__(self, url):
        self.data = []
        self.url = url

    def extract_data_from_page(self, url):
        page = urlopen(url)
        soup = BeautifulSoup(page, features="lxml")
        title = soup.find("div", class_="art_header_title").text
        sub_title = soup.find("div", class_="art_header_sub_title").text
        authors_date = soup.find_all("span", class_="art_header_footer_author")
        authors = authors_date[0].text
        date = re.search(r'\d{2}.\d{2}.\d{2}', authors_date[1].text).group()
        paragraphs = soup.findAll('p')

        for paragraph in paragraphs:
            if not paragraph.find('script') and len(paragraph.text) > 10:
                new_article = [title, sub_title, authors, date, paragraph.text]
                self.data.append(new_article)


    def extract_articles(self, file_name):
        '''
        Crawl articles and create xlsx output file
        :param file_name: output file name
        :return:
        '''
        page = urlopen(self.url)
        soup = BeautifulSoup(page, features="lxml")
        articles = soup.find_all('h4')

        for i, article in enumerate(articles):
            print('\r Crawl {}/{}'.format(str(i+1), len(articles)), end='')
            self.extract_data_from_page("https://www.ynet.co.il" + article.find('a').get('href'))
        print()
        df = pd.DataFrame(self.data, columns=['title', 'sub_title', 'author', 'date', 'content'])
        df.to_excel(file_name)