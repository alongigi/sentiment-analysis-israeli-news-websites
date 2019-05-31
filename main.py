from mako_crawler import MakoCrawler
from Parties import Parties
from party_visualization import PartyVisualization
from ynet_crawler import YnetCrawler
from haaretz_spider import HaaretzCrawler
from party_marker import PartyMarker
import pandas as pd

from sentiment_analyzer import SentimentAnalyzer


def crawler_articles():
    ynet_crawler = YnetCrawler("https://www.ynet.co.il/home/0,7340,L-317,00.html")
    ynet_crawler.extract_articles("ynet.xlsx")
    files_name.append("ynet.xlsx")

    mako_crawler = MakoCrawler("https://www.mako.co.il/news-military/politics")
    mako_crawler.extract_articles("mako.xlsx")
    files_name.append("mako.xlsx")

    haaretzCrawler = HaaretzCrawler()
    haaretzCrawler.extract_articles("haarets")
    files_name.append("haarets.csv")


def mark_parties():
    p = Parties()
    df = p.extract_parties()
    df.to_excel('parties.xlsx')
    pm = PartyMarker('parties.xlsx')
    for file in files_name:
        data = pd.read_excel(file)
        data['Party'] = pm.mark_lines(data['content'])
        data.to_excel(file)


def sentiment_analysis(translated_articles):
    sa = SentimentAnalyzer()
    for file in files_name:
        df = pd.read_excel('translated/' + file)
        df['sentiment'] = sa.analise_texts(df['content_translated'])
        df.to_excel(translated_articles + file)


def visualization(translated_articles):
    pv = PartyVisualization()
    for file in files_name:
        pv.show_plots(translated_articles + file)


if __name__ == "__main__":
    files_name = []
    crawler_articles()
    mark_parties()

    ######################################
    # you have to translate the articles #
    ######################################

    sentiment_analysis('translated/')
    visualization('translated/')


