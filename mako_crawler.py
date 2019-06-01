import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

NUMBER_OF_PAGES = 10

class MakoCrawler:
    def __init__(self, url):
        self.data = []
        self.url = url

    def extract_data_from_page(self, url):
        page = urlopen(url)
        soup = BeautifulSoup(page, features="lxml")
        title = soup.find("h1").text
        sub_title = soup.find("h2").text
        date = soup.find("span", class_="displayDate")

        try:
            date = re.search(r'\d{2}/\d{2}/\d{2}', date.text).group()
        except AttributeError:
            date = ''

        authors = [author["content"] for author in soup.find_all("span", itemprop = 'author')]
        authors = ", ".join(authors)
        paragraphs = soup.findAll('p')

        for paragraph in paragraphs:
            if len(paragraph.text) > 10:
                new_article = [title, sub_title, authors, date, paragraph.text]
                self.data.append(new_article)

    def extract_articles(self, file_name):
        page = urlopen(self.url)
        soup = BeautifulSoup(page, features="lxml")

        page_num = 1
        while page_num < NUMBER_OF_PAGES:
            articles = soup.find_all('h5')
            for i, article in enumerate(articles):
                print('\r Crawl {}/{}'.format(str(i + 1), len(articles)), end='')
                self.extract_data_from_page("https://www.mako.co.il" + article.find('a').get('href'))
            page_num += 1
            url = "https://www.mako.co.il/news-military/politics?page=" + str(page_num)
            page = urlopen(url)
            soup = BeautifulSoup(page, features="lxml")
        print()
        df = pd.DataFrame(self.data, columns=['title', 'sub_title', 'author', 'date', 'content'])
        df.to_excel(file_name)
