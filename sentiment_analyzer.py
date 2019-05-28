from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd


class SentimentAnalyzer:
    def __init__(self):
        self._sentence_analyser = SentimentIntensityAnalyzer()

    def analise(self, text):
        score = self._sentence_analyser.polarity_scores(text)
        pos = score['pos']
        neg = score['neg']
        if pos > neg:
            return 'pos'
        elif pos < neg:
            return 'neg'
        else:
            return 'neu'

    def analise_texts(self, texts):
        return pd.Series(map(self.analise, texts))


df = pd.read_excel('haaretz_articls_28_05_2019_with_party_translated.xlsx')
sa = SentimentAnalyzer()
df['sentiment'] = sa.analise_texts(df['content_translated'])
df.to_excel('haaretz_articls_28_05_2019_with_party_translated_sentiment.xlsx')