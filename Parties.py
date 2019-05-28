from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

class Parties:
    def __init__(self):
        self.data = []

    def extract_parties(self):
        page = urlopen(
            'https://he.wikipedia.org/wiki/%D7%94%D7%91%D7%97%D7%99%D7%A8%D7%95%D7%AA_%D7%9C%D7%9B%D7%A0%D7%A1%D7%AA_%D7%94%D7%A2%D7%A9%D7%A8%D7%99%D7%9D_%D7%95%D7%90%D7%97%D7%AA')
        soup = BeautifulSoup(page, features="lxml")
        ol_tags = soup.find_all('ol')
        for ol in ol_tags:
            number = 0
            for li in ol.find_all('li'):
                if len(li.find('a').text.split(' ')) > 1:
                    number += 1
                    self.data.append([li.find('a').text," ".join(li.parent.parent.parent.parent.find_previous_sibling('tr').find('td').find('b').text.split()[1:]),number])
        return pd.DataFrame(self.data, columns=['Name', 'Party', 'Number'])

# p = Parties()
# page = urlopen('https://he.wikipedia.org/wiki/%D7%94%D7%91%D7%97%D7%99%D7%A8%D7%95%D7%AA_%D7%9C%D7%9B%D7%A0%D7%A1%D7%AA_%D7%94%D7%A2%D7%A9%D7%A8%D7%99%D7%9D_%D7%95%D7%90%D7%97%D7%AA')
# soup = BeautifulSoup(page, features="lxml")
# df = p.extract_parties()
# df.to_excel('parties.xlsx')