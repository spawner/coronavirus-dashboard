import dash_html_components as html
import plotly.graph_objects as go
import requests 

token = ''
api_url = 'https://spawnerapi.com/'

def make_dash_table():
    table = []

    rows = []
    rows.append(html.Td(['S&P 500']))
    rows.append(html.Td(['Markets up today following passing of $2 Trillion stimulus plan.']))

    current_price_url = api_url + 'price' + "/" + 'SPY' + "/" + token
    response = requests.get(current_price_url)
    spy_price = response.json()
    percent_change = spy_price['change']
    percent_change = percent_change*100
    percent_change = round(percent_change, 2)

    if percent_change >= 0: 
        color_change = 'green'
    else: 
        color_change = 'red'
    rows.append(html.Td(['Performance Today: ' + str(percent_change)+"%"], style={'color': color_change}))

    table.append(html.Tr(rows))

    return table


