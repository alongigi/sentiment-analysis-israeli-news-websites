from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd


class SentimentAnalyzer:
    def __init__(self):
        self._sentence_analyser = SentimentIntensityAnalyzer()

    def analise(self, text):
        if type(text) != str:
            return
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
        texts = texts.dropna()
        return pd.Series(map(self.analise, texts))