#!/usr/bin/python
# coding: utf-8

import dash
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
from datetime import datetime as dt
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def get_weather_archive(filename, picked_date):
    df = pd.read_csv(
        filename, 
        usecols=['dt_iso', 'temp', 'wind_speed', 'wind_deg', 'rain_3h', 'snow_3h'])
    df['dt_iso'] = pd.to_datetime(df['dt_iso'])
    df['date'] = pd.to_datetime(df['dt_iso'].apply(lambda x: x.date()))
    df = df.set_index('dt_iso')
    df = df.fillna(0)

    return df[df['date'] == picked_date]

app.layout = html.Div([
        html.Table([
            html.Tr([
                html.Th('Температура, °C'),
                html.Th('Дождь'),
                html.Th('Снег'),
                html.Th('Ветер')
            ]),
            html.Tr([
                html.Td(id='temp-value'),
                html.Td(id='rainfall-value'),
                html.Td(id='snowfall-value'),
                html.Td(
                    id='wind-value',
                    children=html.Img(id='wind-direction'))
            ])
        ]),
        html.Div([
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=dt(2020, 5, 29),
                max_date_allowed=dt(2020, 6, 21),
                date=dt(2020, 5, 29)
            )
        ])
    ])


@app.callback(
    [
        Output('temp-value', 'children'),
        Output('rainfall-value', 'children'),
        Output('snowfall-value', 'children'),
        Output('wind-value', 'children'),
        Output('wind-direction', 'src')
    ],
    [
        Input('my-date-picker-single', 'date')
    ]
)
def get_weather_data(date):
    df = get_weather_archive('data//weather_archive.csv', date)
    direction = 'n'
    # if (df['wind_deg'] >= 0 and df['wind_deg'] <= 23) or (df['wind_deg'] >= 333 and df['wind_deg'] <= 360):
    #     direction = 'n'
    # elif df['wind_deg'] > 23 and df['wind_deg'] <= 67:
    #     direction = 'ne'
    # elif df['wind_deg'] > 67 and df['wind_deg'] <= 112:
    #     direction = 'e'
    # elif df['wind_deg'] > 112 and df['wind_deg'] <= 156:
    #     direction = 'se'
    # elif df['wind_deg'] > 156 and df['wind_deg'] <= 200:
    #     direction = 's'
    # elif df['wind_deg'] > 200 and df['wind_deg'] <= 244:
    #     direction = 'sw'
    # elif df['wind_deg'] > 244 and df['wind_deg'] <= 288:
    #     direction = 'w'
    # elif df['wind_deg'] > 288 and df['wind_deg'] < 333:
    #     direction = 'nw'
    img_source = app.get_asset_url(direction + '.jpg')  
    return ([
        df['temp'],
        df['rain_3h'],
        df['snow_3h'],
        df['wind_speed'],
        img_source
    ])



if __name__ == '__main__':
    app.run_server(debug=True)