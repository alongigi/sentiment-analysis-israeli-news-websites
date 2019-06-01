from mako_crawler import MakoCrawler
from Parties import Parties
from party_visualization import PartyVisualization
from ynet_crawler import YnetCrawler
from haaretz_spider import HaaretzCrawler
from party_marker import PartyMarker
import pandas as pd
import os
from bokeh.layouts import column
from bokeh.io import output_file, show
from sentiment_analyzer import SentimentAnalyzer


def crawler_articles():
    print('Crawl ynet')
    ynet_crawler = YnetCrawler("https://www.ynet.co.il/home/0,7340,L-317,00.html")
    ynet_crawler.extract_articles("crawled/ynet.xlsx")
    files_name.append("crawled/ynet.xlsx")
    print('Crawl mako')
    mako_crawler = MakoCrawler("https://www.mako.co.il/news-military/politics")
    mako_crawler.extract_articles("crawled/mako.xlsx")
    files_name.append("crawled/mako.xlsx")
    print('Crawl haaretz')
    haaretzCrawler = HaaretzCrawler()
    haaretzCrawler.extract_articles("crawled/haarets")
    files_name.append("crawled/haarets.xlsx")


def mark_parties():
    p = Parties()
    df = p.extract_parties()
    df.to_excel('parties.xlsx')
    pm = PartyMarker('parties.xlsx')
    file_names = os.listdir('crawled/')
    for i, file in enumerate(file_names):
        print('\r mark parties for {}, {}/{}'.format(file, str(i + 1), len(file_names)), end='')
        data = pd.read_excel(file)
        data['Party'] = pm.mark_lines(data['content'])
        data.to_excel(file)
    print()


def sentiment_analysis(translated_articles):
    sa = SentimentAnalyzer()
    file_names = os.listdir(translated_articles)
    for i, file in enumerate(file_names):
        print('\r generate sentiment for {}, {}/{}'.format(file, str(i+1), len(file_names)), end='')
        df = pd.read_excel('translated/' + file)
        df['sentiment'] = sa.analise_texts(df['content_translated'])
        df.to_excel(translated_articles + file)
    print()


def visualization(translated_articles):
    pv = PartyVisualization()
    rows = []
    file_names = os.listdir(translated_articles)
    for i, file in enumerate(file_names):
        print('\r generate visualization for {}, {}/{}'.format(file, str(i + 1), len(file_names)), end='')
        rows.append(pv.show_plots(translated_articles + file))
    print()
    show(column(*rows))


if __name__ == "__main__":
    files_name = []
    # print('Crawl data')
    # crawler_articles()
    # print('Mark parties')
    # mark_parties()

    ######################################
    # you have to translate the articles #
    ######################################
    print('Start sentiment analysis')
    sentiment_analysis('translated/')
    print('Generate visualization')
    visualization('translated/')


