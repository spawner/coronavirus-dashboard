import dash
import pandas as pd
import numpy as np
import json 
import requests
import textwrap 

import pathlib
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go

from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from helpers import make_dash_table


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

DATA_PATH = pathlib.Path(__file__).parent.joinpath("data").resolve()

ticker_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
ticker_df = ticker_df[0]
ticker_series = ticker_df["Symbol"]
ticker_list = list(ticker_series)
ticker_list.append('TSLA')

# Replace token with your token, obtained from https://spawner.ai/register
api_url = 'https://spawnerapi.com/'
token = ''

STARTING_EQUITY = "SPY"
EQUITY_DESCRIPTION = "SPY is an ETF tracking the S&P 500."
img = 'assets/spdr.png'
EQUITY_IMG = img

current_price_url = api_url + 'price' + "/" + STARTING_EQUITY + "/" + token
response = requests.get(current_price_url)
spy_price = response.json()
current_price = spy_price['price']
price_change = spy_price['change']
price_change = price_change*100
price_change = round(price_change, 2)

price_history_url = api_url + 'price-history' + "/" + STARTING_EQUITY + "/" + '3m' + "/" + token
response = requests.get(price_history_url)
price_history_json = response.json()
price_history_json = json.dumps(price_history_json)
price_history_DF = pd.read_json(price_history_json, orient='records')


### chart 
fig = go.Figure()
fig.add_trace(go.Scatter(
        x=price_history_DF["date"],
        y=price_history_DF["close"],
        name=STARTING_EQUITY,
        line_color='rgba(31,119,180,1)'))

fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis={'title': 'Date','fixedrange':True}, yaxis={'title': 'Price','fixedrange':True}, plot_bgcolor='rgb(250,250,250)', margin={'t': 15, 'b': 9},width=600,height=300)

app.layout = html.Div(
    [
    html.A([
            html.Img(
                src=app.get_asset_url("spawner.png"), 
                style={'height':'8%', 'width':'8%'})
        ], className="app__banner", href='https://spawner.ai', target="_blank"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Coronavirus Crash Tracker",
                                    className="title",
                                ),
                                html.Span(
                                    "Keep ahead of the markets in these volatile times."
                                ),
                                html.Br(),
                                html.A("Access Financial Data and Machine Learning to build your own dashboard.", href="https://spawner.ai", target="_blank"),
                            ]
                        )
                    ],
                    className="app__header",
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="chem_dropdown",
                            multi=False,
                            options=[{"label": i, "value": i} for i in ticker_list],
                            placeholder="Select a ticker...",
                        )
                    ],
                    className="app__dropdown",
                ),
                html.Div(
                    [
                        html.Table(
                            make_dash_table(),
                            id="table-element",
                            className="table__container",
                        )
                    ],
                    className="container bg-white p-0",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H5(
                                    "Price history since before the panic (~Feb. 20th)",
                                ),
                                html.H6(
                                    id="quote-and-change",
                                    children="SPY: $" + str(current_price) + "(" + str(price_change) + "%" + ")",
                                    className="data"

                                ),
                                dcc.Graph(
                                    id="clickable-graph",
                                    className="chart-graph",
                                    figure=fig, 
                                    config={'displayModeBar': False, 'scrollZoom': False}
                                ),
                                html.Span(
                                    children="Cash Flow: ",
                                    id="Cash-Flow2",
                                    className="title"
                                ),
                                html.Span(
                                    children="N/A",
                                    id="Cash-Flow",
                                    className="data"

                                ),
                                html.Br(),
                                html.Span(
                                    children="Current Ratio: ",
                                    id="Current-Ratio2",
                                    className="title"
                                ),
                                html.Span(
                                    children="N/A",
                                    id="Current-Ratio",
                                    className="data"
                                    
                                ),
                                html.Br(), 
                                html.Span(
                                    children="Debt-Equity: ",
                                    id="Debt-Equity2",
                                    className="title"
                                ),
                                html.Span(
                                    children="N/A",
                                    id="Debt-Equity",
                                    className="data"
                                ),
                                html.Br(),
                                html.Span(
                                    children="Status: ",
                                    id="Health2",
                                    className="title"
                                ),
                                html.Span(
                                    children="N/A",
                                    id="Health",
                                    className="data"
                                ),
                                html.Br(),
                                html.Span(
                                    children="Reason: ",
                                    id="Reason2",
                                    className="title"
                                ),
                                html.Span(
                                    children="N/A",
                                    id="Reason",
                                    className="data"
                                ),
                                html.Br(),
                            ],
                            className="two-thirds column",
                        ),
                    ],
                    className="container card app__content bg-white",
),html.Br(),
                    html.Div(
                    [
                        html.Div(
                        [
                                html.Br(),
                                html.Br(),

                                html.Span(" Built by the team at ",className="bold"),
                                html.A("Spawner.ai", href="https://spawner.ai", target="_blank"),
                                html.Span(". In this dashboard we use Machine Learning to classify health of equity based on metrics like liquidity, debt, credit, and more vs historical performance in downturn. A company with a rating of Healthy is very likely to make it through a downturn. As long as the economy remains unstable we will continue to provide and update this data free of charge."),
                        ])
                    ], className="container p-0",
)
                
                
                

            ],
            className="app__container",
        ),
    ]
)

@app.callback(
    Output("clickable-graph", "figure"),
    [Input("chem_dropdown", "value")],
)
def highlight_molecule(ticker_dropdown_value):
    price_history_url = api_url + 'price-history' + "/" + ticker_dropdown_value + "/" + '3m' + "/" + token
    response = requests.get(price_history_url)
    price_history_json = response.json()
    price_history_json = json.dumps(price_history_json)
    price_history_DF = pd.read_json(price_history_json, orient='records')

    date = price_history_DF["date"]
    close = price_history_DF["close"]
    ticker = ticker_dropdown_value
    fig = go.Figure()
    fig.add_trace(go.Scatter(
            x=date,
            y=close,
            name=ticker,
            line_color='rgba(31,119,180,1)'))
    fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False, xaxis={'title': 'Date','fixedrange':True}, yaxis={'title': 'Price','fixedrange':True}, plot_bgcolor='rgb(250,250,250)', margin={'t': 15, 'b': 9},width=600,height=300)
    return (
        fig
    )


@app.callback(
    Output("quote-and-change", "children"),
    [Input("chem_dropdown", "value")],
)
def price_and_change(ticker_dropdown_value):

    current_price_url = api_url + 'price' + "/" + ticker_dropdown_value + "/" + token
    response = requests.get(current_price_url)
    price = response.json()
    current_price = price['price']
    price_change = price['change']
    price_change = price_change*100
    price_change = round(price_change, 2)

    print(price_change)
    print(current_price)

    output_value = ticker_dropdown_value + ": " + "$" + str(current_price) + " (" + str(price_change) + "%)"

    return (
        output_value
    )

@app.callback(
    [                                  
        Output("Cash-Flow", "children"),
        Output("Current-Ratio", "children"),
        Output("Debt-Equity", "children"),
        Output("Health", "children"),
        Output("Reason", "children"),
        Output("Cash-Flow", "style"),
        Output("Current-Ratio", "style"),
        Output("Debt-Equity", "style"),
        Output("Health", "style"),
    ],
    [Input("chem_dropdown", "value")],
)
def update_health(ticker_dropdown_value):
    token = 'sp_4d6f6ef2698976bf3ae87e05532af60c'
    url = "https://spawnerapi.com/health/" + ticker_dropdown_value + "/" + token
    response = requests.get(url)
    response = response.json()
    cash_flow = response[0]['cash_flow']
    cash_flow = round(cash_flow, 2)
    if cash_flow < 0: 
        cash_flow_style = {'color': 'red'}
    else: 
        cash_flow_style = {'color': 'green'}
    cash_flow = str(cash_flow)
    
    current_ratio = response[0]['current_ratio']
    current_ratio = round(current_ratio, 2)
    if current_ratio <= 1: 
        current_ratio_style = {'color': 'red'}
    else: 
        current_ratio_style = {'color': 'green'}
    current_ratio = str(current_ratio)
    debt_equity = response[0]['debt_equity']
    debt_equity = round(debt_equity, 2)
    if debt_equity <= 1.8 and debt_equity >= 0: 
        debt_ratio_style = {'color': 'green'}
    else: 
        debt_ratio_style = {'color': 'red'}
    debt_equity = str(debt_equity)
    health = response[0]['health']
    if health == 'Moderately Healthy' or health == 'Healthy':
        health_style = {'color': 'green'}
        reason_text = "Our algorithm classified this as healthy for a combination of decent to good debt, liquidity, available credit, and more (excluding potential govt. assistance)."
    else: 
        health_style = {'color': 'red'}
        reason_text = "Our algorithm classified this as unhealthy for a combination of decent to bad debt, liquidity, available credit, and more (excluding potential govt. assistance)."
    return (
        cash_flow,
        current_ratio,
        debt_equity,
        health,
        reason_text,
        cash_flow_style,
        current_ratio_style,
        debt_ratio_style,
        health_style,
    )


def update_table():
    return make_dash_table()
update_table()

if __name__ == "__main__":
    app.run_server(debug=True)
