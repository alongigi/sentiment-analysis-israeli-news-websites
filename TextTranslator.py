import json

from py_translator import Translator
import pandas as pd


class TextTranslator:
    def __init__(self, source_language='he', destination_language='en'):
        self._translator = Translator()
        self._src_lang = source_language
        self._dest_lang = destination_language

    def translate(self, text):
        try:
            return self._translator.translate(text, self._dest_lang, self._src_lang).text
        except json.decoder.JSONDecodeError as e:
            return text


    def translate_lines(self, texts):
        translations = []
        for i, text in enumerate(texts):
            print('\rtranslate {}/{}'.format(str(i + 1), len(texts)), end='')
            translations.append(self.translate(text))
        print()
        return translations


t = TextTranslator()
print(t.translate('hello mom'))
data = pd.read_csv('haaretz_articls_15_05_2019.csv')
data['content'] = t.translate_lines(data['content'])
data.to_csv('haaretz_articls_15_05_2019_translated.csv')
