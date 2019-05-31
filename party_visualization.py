from math import pi
from collections import defaultdict, Counter
import pandas as pd
from bokeh.layouts import row
from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum


class PartyVisualization:
    def __init__(self):
        output_file("pie.html")

    def show_plots(self, file_name):
        df = pd.read_excel(file_name)
        party_sentiment_df = df[['Party', 'sentiment']]
        party_sentiment_df.dropna(inplace=True)
        party_Sentiment_dict = defaultdict(list)
        for parties, sentiment in party_sentiment_df.to_records(index=False):
            for party in map(str.strip, parties.split(', ')):
                party_Sentiment_dict[party].append(sentiment)
        pass

        Category20c[1] = Category20c[3][:1]
        Category20c[2] = Category20c[3][:2]
        plots = []
        for party in party_Sentiment_dict:
            plots.append(self.create_plot(party, party_Sentiment_dict))
        show(row(*plots))

    def create_plot(self, party, party_Sentiment_dict):
        x = Counter(party_Sentiment_dict[party])
        data = pd.Series(x).reset_index(name='value').rename(columns={'index': 'country'})
        data['angle'] = data['value'] / data['value'].sum() * 2 * pi
        data['color'] = Category20c[len(x)]

        p = figure(plot_height=250, title=party, toolbar_location=None,
                   tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

        p.wedge(x=0, y=1, radius=0.2,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color="white", fill_color='color', legend='country', source=data)

        p.axis.axis_label = None
        p.axis.visible = False
        p.grid.grid_line_color = None
        return p
# show(p)