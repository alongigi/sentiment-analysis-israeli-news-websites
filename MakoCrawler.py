import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

NUMBER_OF_PAGES = 30

def extract_data_from_page(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, features="lxml")

    new_article = []
    title = soup.find("h1").text
    sub_title = soup.find("h2").text
    date = soup.find("span", class_="displayDate")
    try:
        date = re.search(r'\d{2}/\d{2}/\d{2}', date.text).group()
    except AttributeError:
        date = ''
    authors = [author["content"] for author in soup.find_all("span", itemprop = 'author')]
    authors = ", ".join(authors)

    new_article.append(title)
    new_article.append(sub_title)
    new_article.append(authors)
    new_article.append(date)
    text = ""

    paragraphs = soup.findAll('p')
    for paragraph in paragraphs:
        text += paragraph.text

    new_article.append(text)
    data.append(new_article)

data = []
url = "https://www.mako.co.il/news-military/politics"
page = urlopen(url)
soup = BeautifulSoup(page, features="lxml")

page_num = 1
while page_num < NUMBER_OF_PAGES:
    articles = soup.find_all('h5')
    for article in articles:
        extract_data_from_page("https://www.mako.co.il" + article.find('a').get('href'))
    page_num += 1
    url = "https://www.mako.co.il/news-military/politics?page=" + str(page_num)
    page = urlopen(url)
    soup = BeautifulSoup(page, features="lxml")

df = pd.DataFrame(data, columns=['title', 'sub_title', 'author', 'date', 'text'])
df.to_excel('mako.xlsx')
