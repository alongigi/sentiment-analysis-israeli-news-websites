import pandas as pd
from collections import Counter
import os
from party_visualization import PartyVisualization
import parse


class StatisticExtractor:

    def __init__(self, output_path):
        self.author_statistics_rows = []
        self.paragraph_statistics_rows = []
        self._output_path = output_path

    def get_sentiment_statistics(self, author_sentiment):
        '''
        Calc if a row in df is pos, neg or neu
        :param author_sentiment:
        :return: pos, neg, neu counts
        '''
        pos, neg, neu = 0, 0, 0
        for record in author_sentiment.to_records(index=False):
            if record['pos'] > record['neg']:
                pos += 1
            elif record['pos'] < record['neg']:
                neg += 1
            else:
                neu += 1
        return pos, neg, neu

    def extract_statistics_for_files(self, translated_articles):
        '''
        Extract statistics for all list of files
        :param translated_articles:
        :return:
        '''
        self.author_statistics_rows = []
        self.paragraph_statistics_rows = []
        file_names = os.listdir(translated_articles)
        for path in file_names:
            self.extract_statistics(os.path.join(translated_articles, path), parse.parse('{}.xlsx', path)[0])
        columns_names = ['website', 'pos_author', 'neg_author', 'neu_author', 'pos_author_frac', 'neg_author_frac',
                         'neu_author_frac']
        output_file_name = 'author_statistics.xlsx'
        rows = self.author_statistics_rows
        self._create_sentiment_statistics(columns_names, output_file_name, rows)

        columns_names = ['website', 'pos_paragraph', 'neg_paragraph', 'neu_paragraph', 'pos_paragraph_frac',
                         'neg_paragraph_frac', 'neu_paragraph_frac']
        output_file_name = 'paragraph_statistics.xlsx'
        rows = self.paragraph_statistics_rows
        self._create_sentiment_statistics(columns_names, output_file_name, rows)

    def _create_sentiment_statistics(self, columns_names, output_file_name, rows):
        author_statistics_rows = [
            (party, pos, neg, neu, pos / sum([pos, neg, neu]), neg / sum([pos, neg, neu]), neu / sum([pos, neg, neu]))
            for party, pos, neg, neu in rows]
        pd.DataFrame(author_statistics_rows,
                     columns=columns_names).to_excel(
            os.path.join(self._output_path, output_file_name), index=False)

    def extract_statistics(self, path, file_name):
        '''
        Calc and creat statistic for input file
        :param path: file path
        :param file_name: file name
        :return:
        '''
        df = pd.read_excel(path)

        author_sentiment = df.groupby('author')['sentiment'].value_counts().unstack().fillna(0)
        assert isinstance(author_sentiment, pd.DataFrame)

        pos_authors, neg_authors, neu_authors = self.get_sentiment_statistics(author_sentiment)
        self.author_statistics_rows.append((file_name, pos_authors, neg_authors, neu_authors))
        paragraph_sentiment = df.groupby(df.index)['sentiment'].value_counts().unstack().fillna(0)
        pos_paragraph, neg_paragraph, neu_paragraph = self.get_sentiment_statistics(paragraph_sentiment)
        self.paragraph_statistics_rows.append((file_name, pos_paragraph, neg_paragraph, neu_paragraph))

        pv = PartyVisualization()
        party_sentiment_dict = pv.get_party_sentiment_dict(df)
        party_sentiment_rows = []
        for party, sentiments in party_sentiment_dict.items():
            x = Counter(sentiments)
            total = len(sentiments)
            party_sentiment_rows.append((party, x.get('pos', 0), x.get('neg', 0), x.get('neu', 0)
                                         , x.get('pos', 0) / total, x.get('neg', 0) / total, x.get('neu', 0) / total))
        pd.DataFrame(party_sentiment_rows,
                     columns=['party', 'pos_paragraph', 'neg_paragraph', 'neu_paragraph'
                         , 'pos_paragraph_frac', 'neg_paragraph_frac', 'neu_paragraph_frac']).to_excel(
            os.path.join(self._output_path, file_name + '.xlsx'), index=False, )


pass
