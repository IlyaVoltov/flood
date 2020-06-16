#!/usr/bin/env python
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy  as np

app = dash.Dash(__name__)
server = app.server
first_june = pd.read_csv('C:\\Users\ИТ ФИЦ\Desktop\BI Разлив\Разлив - Лист1.csv',
                         usecols = ['date', 'time_start', 'time_end',
                                    'lon', 'lat', 'val', 'standard', 'cluster']) 

input_data = first_june.replace(',', '.', regex = True)
input_data.iloc[:, 3:] = input_data.iloc[:, 3:].astype('float64')
input_data['excess'] = input_data.val / input_data.standard

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

fig_map = px.scatter_mapbox(data_frame = input_data,
                            lat = 'lat',
                            lon = 'lon',
                            animation_frame = 'date',
                            color_continuous_scale = 'Bluered',
                            range_color = [0, 10],
                            color = 'excess',
                            width = 900,
                            height = 800 )

fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 700

fig_map.update_layout(
                  hovermode = 'closest',
                  hoverlabel = dict(
                                    bgcolor = 'black', 
                                    font_size = 10, 
                                    font_family = 'Helvetica',
                                    font_color = 'white'
                                    ),
                  mapbox = dict(
                                accesstoken = access,
                                bearing = 0,
                                center = go.layout.mapbox.Center(
                                         lat = 69.666084,
                                         lon = 87.791365
                                         ),
                  pitch = 0,
                  zoom = 7,   
                  style = 'outdoors'   
    )
)

app.layout = html.Div(
                      children = [ 
                       dcc.Graph(id = 'int_map', figure = fig_map),
])


def create_time_series(dff):
    return {
            'data': [dict(
                          x = dff['Year'],
                          y = dff['Value'],
                          mode = 'lines+markers'
                          )
                    ],
            'layout': {
                        'height': 225,
                        'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
                        'annotations': [{
                                         'x': 0, 
                                         'y': 0.85, 
                                         'xanchor': 'left', 
                                         'yanchor': 'bottom',
                                         'xref': 'paper', 
                                         'yref': 'paper', 
                                         'showarrow': False,
                                         'align': 'left', 
                                         'bgcolor': 'rgba(255, 255, 255, 0.5)',
                                         'text': title
                                        }]
        }
    }



def update_y_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['Country Name'] == country_name]
    dff = dff[dff['Indicator Name'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)


if __name__ == '__main__':
    app.run_server(debug = True)





