import pandas as pd


class PartyMarker:
    def __init__(self, party_file_path='parties.xlsx'):
        parties_data = pd.read_excel(party_file_path)
        party_member_dict = dict(list(parties_data.groupby('Party')['Name']))
        self._member_party_dict = {}
        for party, members in party_member_dict.items():
            self._member_party_dict[party] = party
            self._member_party_dict.update({member: party for member in members})

    def mark(self, text):
        parties = []
        for member, party in self._member_party_dict.items():
            if member in text:
                parties.append(party)
        return ' | '.join(parties)

    def mark_lines(self, texts):
        return pd.Series(texts).apply(self.mark)


pm = PartyMarker('parties.xlsx')
data = pd.read_csv('haaretz_articls_15_05_2019.csv')
data['Party'] = pm.mark_lines(data['content'])
data.to_excel('haaretz_articls_15_05_2019_with_party.xlsx')
