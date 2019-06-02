import pandas as pd
import numpy as np

class PartyMarker:
    def __init__(self, party_file_path='parties.xlsx'):
        parties_data = pd.read_excel(party_file_path)
        party_member_dict = dict(list(parties_data.groupby('Party')['Name']))
        self._member_party_dict = {}
        for party, members in party_member_dict.items():
            self._member_party_dict[party] = party
            self._member_party_dict.update({member: party for member in members})

    def mark(self, text):
        '''
        return parties inside text
        :param text: content
        :return: parties separated by ' | '
        '''
        if type(text) != str:
            return
        parties = set()
        for member, party in self._member_party_dict.items():
            if member in text:
                parties.add(party)
        return ' | '.join(parties)

    def mark_lines(self, texts):
        '''
        return parties inside text for list of texts
        :param texts: contents
        :return: Series(parties)
        '''
        return pd.Series(texts).apply(self.mark)
