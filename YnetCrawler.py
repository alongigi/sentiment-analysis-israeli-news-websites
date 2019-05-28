import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

from Parties import Parties

def extract_data_from_page(url):
    page = urlopen(url)
    soup = BeautifulSoup(page, features="lxml")

    title = soup.find("div", class_="art_header_title").text
    sub_title = soup.find("div", class_="art_header_sub_title").text
    authors_date = soup.find_all("span", class_="art_header_footer_author")
    authors = authors_date[0].text
    date = re.search(r'\d{2}.\d{2}.\d{2}', authors_date[1].text).group()

    paragraphs = soup.findAll('p')
    for paragraph in paragraphs:
        if not paragraph.find('script') and len(paragraph.text) > 5:
            knesset_members = []
            parties = []
            for party in df_parties['Party'].unique():
                if party in paragraph.text:
                    parties.append(party)
            for index, row in df_parties.iterrows():
                if row['Name'] in paragraph.text:
                    knesset_members.append(row['Name'])
                    if row['Party'] not in parties:
                        parties.append(row['Party'])
            new_article = [title, sub_title, authors, date, paragraph.text, ', '.join(knesset_members), ', '.join(parties)]
            data.append(new_article)


p = Parties()
df_parties = p.extract_parties()

data = []
url = "https://www.ynet.co.il/home/0,7340,L-317,00.html"
page = urlopen(url)
soup = BeautifulSoup(page, features="lxml")

articles = soup.find_all('h4')
for article in articles:
    extract_data_from_page("https://www.ynet.co.il" + article.find('a').get('href'))

hrefs = soup.find_all('a')

for href in hrefs:
    if href.text == 'כתבות נוספות':
        url = href.get('href')
        break
page = urlopen(url)
soup = BeautifulSoup(page, features="lxml")


articles = soup.find_all("a", class_="smallheader")

for article in articles:
    try:
        extract_data_from_page("https://www.ynet.co.il" + article.get('href'))
    except AttributeError:
        pass


df = pd.DataFrame(data, columns=['title', 'sub_title', 'author', 'date', 'text', 'Knesset_Members', 'Parties'])
df.to_excel('ynet.xlsx')