import dash_html_components as html
import pandas as pd

def generate_weather_table():
    weather_table = html.Div([
        html.Table([
            html.Tr([
                html.Th('Температура, °C'),
                html.Th('Осадки'),
                html.Th('Ветер')
            ]),
            html.Tr([
                html.Td(id='temp-value'),
                html.Td(id='rainfall-value'),
                html.Td(
                    id='wind-value',
                    children=html.Img(id='wind-direction'))
            ])
        ]),
    ])


@app.callback(
    
)