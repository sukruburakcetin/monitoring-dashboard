import dash
from dash.dependencies import Output, Input, State
from dash import Dash, dcc, html, callback
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import json
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")
import pathlib
import psycopg2
import geopandas as gpd
from geopandas import GeoDataFrame
import plotly


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )
access_token = 'pk.eyJ1IjoiYWJkdWxrZXJpbW5lc2UiLCJhIjoiY2s5aThsZWlnMDExcjNkcWFmaWUxcmh3YyJ9.s-4VLvmoPQFPXdu9Mcd6pA'
px.set_mapbox_access_token(access_token)

# conn = psycopg2.connect(database="postgres", user='postgres', password='cbs2022', host='127.0.0.1', port= '5432',
#                         options="-c search_path=dbo,toys_monitoring")
# cursor = conn.cursor()

# with open(r"assets\data\tr-cities.json",encoding='utf-8') as response:
#     turkey_city= json.load(response)
turkey_city = gpd.read_file(r"assets\data\tr-cities.json")
turkey_city = GeoDataFrame(turkey_city, crs="EPSG:4326")

# list_df= []
#
# cursor.execute("""SELECT * FROM turkiye_nufus_2021""")
# for table in cursor.fetchall():
#     list_df.append(table)
# tr_nufus = pd.DataFrame(list_df, columns =['Il', 'Erkek', 'Kadin','Toplam','number'])
tr_nufus = pd.read_excel(r"assets\data\tr_nufus_21.xls")



app.layout = dbc.Container([
    #INDICATORS
    dbc.Row([
        dbc.Col([dcc.Graph(id='left_indicator',figure={})],xs=12, sm=12, md=4, lg=4, xl=4),
        dbc.Col([dcc.Graph(id='middle_indicator',figure={})],xs=12, sm=12, md=4, lg=4, xl=4),
        dbc.Col([dcc.Graph(id='right_indicator',figure={})],xs=12, sm=12, md=4, lg=4, xl=4)
    ]),
    #MAP
    dbc.Row([
        dbc.Col([],xs=0, sm=0),
        dbc.Col([dcc.Graph(id="map",figure={})],xs=12, sm=12, md=12, lg=12, xl=12),
        dbc.Col([],xs=0, sm=0)
    ]),
    html.Br(),
    #CHARTS
    dbc.Row([
        dbc.Col([dcc.Graph(id='left_chart',figure={})],xs=12, sm=12, md=4, lg=4, xl=4),
        dbc.Col([dcc.Graph(id='middle_chart',figure={})],xs=12, sm=12, md=4, lg=4, xl=4),
        dbc.Col([dcc.Graph(id='right_chart',figure={})],xs=12, sm=12, md=4, lg=4, xl=4)
    ]),
    dcc.Interval(
    id='interval-component',
    interval=1 * 10000000,  # in milliseconds
    n_intervals=0
)

],style={'background-color':'#121212'},fluid=True)


@app.callback(
    Output('left_indicator','figure'),
    Output('middle_indicator','figure'),
    Output('right_indicator','figure'),
    Output('map','figure'),
    Output('left_chart','figure'),
    Output('middle_chart','figure'),
    Output('right_chart','figure'),
    Input(component_id='interval-component', component_property='n_intervals')
)

def update_graph(option_slctd):
    # LEFT INDICATOR
    top_nufus = tr_nufus['Toplam'].sum()
    fig_left_indicator = go.Figure(go.Indicator(
        title={
            'text': 'TOPLAM NÜFUS ',
            'font': {'size': 17},
        },
        mode="number",
        value=int(top_nufus),

    ))
    fig_left_indicator.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font=dict(color="white"))

    # MIDDLE INDICATOR
    erkek_nufus = tr_nufus['Erkek'].sum()
    fig_middle_indicator = go.Figure(go.Indicator(
        title={
            'text': 'Erkek NÜFUS',
            'font': {'size': 17},
        },
        mode="number",
        value=int(erkek_nufus),

    ))
    fig_middle_indicator.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font=dict(color="white"))

    # RIGHT INDICATOR
    kadin_nufus = tr_nufus['Kadin'].sum()
    fig_right_indicator = go.Figure(go.Indicator(
        title={
            'text': 'KADIN NÜFUS',
            'font': {'size': 17},
        },
        mode="number",
        value=int(kadin_nufus),

    ))
    fig_right_indicator.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font=dict(color="white"))

    #MAP
    fig = px.choropleth_mapbox(tr_nufus, geojson=turkey_city,
                                   locations="number",
                                   color="Toplam",
                                   hover_name="Il",
                                   featureidkey="properties.number",
                                   # animation_frame="YIL",
                                   color_continuous_scale='blues',
                                   #               mapbox_style="carto-positron",
                                   mapbox_style="dark",
                                   zoom=5, center={"lat":38.535, "lon": 35.173},
                                   #               opacity=0.5,
                                   labels={'Il': 'İL', 'Toplam': 'TOPLAM NÜFUS','number':'İL PLAKA KODU'}
                                   )
    fig.update_layout(
    # height=400,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    plot_bgcolor="#121212",
    paper_bgcolor="#121212",
    font=dict(color="white"))
    # fig.show()

    #LEFT CHART

    top_otuz = tr_nufus[['Toplam', 'Il']].sort_values('Toplam', ascending=False).head(30)
    fig_left_chart = px.bar(top_otuz,x='Toplam',y='Il',color='Toplam',
                            # height=700,
           title='NÜFUSU EN ÇOK OLAN İLK OTUZ İL',color_continuous_scale=plotly.express.colors.sequential.Blugrn)
    fig_left_chart.update_layout(plot_bgcolor="#121212",paper_bgcolor="#121212",# margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                 font=dict(color="white"))


    #MIDDLE CHART
    gender_df = pd.melt(tr_nufus[["Il","Erkek","Kadin"]], id_vars=['Il'],var_name='gender', value_name='value')
    fig_middle_chart = px.pie(gender_df, values='value', names='gender',hole=.6,
                     labels={'value': 'NÜFUS', 'gender': 'CİNSİYET', 'ILCE': 'İLÇE'},
                     # height=600

                     )
    fig_middle_chart.update_layout(title=f'CİNSİYETE GÖRE TOPLAM NÜFUS', plot_bgcolor="#121212",
                          paper_bgcolor="#121212",
                          # margin={"r": 0, "t": 0, "l": 0, "b": 0},
                          font=dict(color="white"))

    #RIGHT CHART
    son_otuz = tr_nufus[['Toplam', 'Il']].sort_values('Toplam', ascending=True).head(30)
    fig_right_chart = px.bar(son_otuz, x='Toplam', y='Il', color='Toplam',
                             # height=700,
                 title='NÜFUSU AZ OLAN SON OTUZ İL',
                 color_continuous_scale=plotly.express.colors.sequential.OrRd)
    fig_right_chart.update_layout(plot_bgcolor="#121212",paper_bgcolor="#121212",# margin={"r": 0, "t": 0, "l": 0, "b": 0},
                                 font=dict(color="white"))

    return fig_left_indicator, fig_middle_indicator, fig_right_indicator, fig, fig_left_chart, fig_middle_chart, fig_right_chart


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=1234)
    # app.run_server(debug=True, port=1234)


print("adaw")



