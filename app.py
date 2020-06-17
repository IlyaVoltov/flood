#!/usr/bin/env python
# coding: utf-8

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import json

app = dash.Dash(__name__)
server = app.server
first_june = pd.read_csv('data\\Разлив - Лист1.csv',
                         usecols=['date', 'time_start', 'time_end',
                                    'lon', 'lat', 'val', 'standard', 'cluster']) 

input_data = first_june.replace(',', '.', regex=True)
input_data.iloc[:, 3:] = input_data.iloc[:, 3:].astype('float64')
input_data['excess'] = input_data.val / input_data.standard

data_table = pd.read_csv('data\\Разлив - Лист2.csv')


def line_json(file_path):
    openfile = open(file_path)
    jsondata = json.load(openfile)
    df = pd.DataFrame(jsondata)
    openfile.close()
    
    geocode = df.loc['coordinates', 'geometry']
    geo_lon = []
    geo_lat = []
    for geo_inst in geocode:
        geo_lon.append(geo_inst[0]) 
        geo_lat.append(geo_inst[1])
    
    return [geo_lon, geo_lat]


def poly_json(file_path):
    openfile = open(file_path)
    jsondata = json.load(openfile)
    df = pd.DataFrame(jsondata)
    openfile.close()
    
    geocode = df.loc['coordinates', 'geometry'][0]
    geo_lon = []
    geo_lat = []
    for geo_inst in geocode:
        geo_lon.append(geo_inst[0]) 
        geo_lat.append(geo_inst[1])
    
    return [geo_lon, geo_lat]

bon1       = line_json(file_path = 'data\\bon1.json')
bon2       = line_json(file_path = 'data\\bon2.json')
camp_geo   = poly_json(file_path = 'data\\camp.json')
pyasino    = poly_json(file_path = 'data\\pyasino.json')
norilskaya = poly_json(file_path = 'data\\norilskaya.json')
ambarnaya  = poly_json(file_path = 'data\\ambarn.json')
ambar2     = poly_json(file_path = 'data\\amb2.json')
ambar3     = poly_json(file_path = 'data\\amb3.json')
ambar4     = poly_json(file_path = 'data\\amb4.json')
daldykan   = poly_json(file_path = 'data\\daldykan.json')
ambar5     = poly_json(file_path = 'data\\amb5.json')

markersize = []
color_list = []
for exc in input_data.excess:
    if exc <= 1:
        color_list.append('limegreen')
        markersize.append(7)
    elif exc >= 1.001 and exc <= 10:
        color_list.append('yellow')
        markersize.append(10)
    elif exc >= 10.001 and exc <= 100:
        color_list.append('darkorange')
        markersize.append(12)
    elif exc >= 100.001 and exc <= 1000:
        color_list.append('fuchsia')
        markersize.append(14)
    elif exc >= 100.001 and exc <= 1000:
        color_list.append('darkpurple')
        markersize.append(14)
    else:
        color_list.append('red')
        markersize.append(20)


access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'


# Карта  с отмеченными отборами воды
figure = go.Figure(go.Scattermapbox(
                lat = input_data.lat,
                lon = input_data.lon,
                mode = 'markers',
                customdata = input_data,
                hovertemplate = 'Результат отбора : %{customdata[5]:.2f} мг/дм3' +
                                '<br>Превышение нормы в %{customdata[8]:.1f} раз</br>' +
                                '<br>Дата отбора : %{customdata[0]}'
                                '<br>Время начала отбора : %{customdata[1]}' +
                                '<br>Время окончания отбора : %{customdata[2]}',
                name = 'Отборы воды',
                marker = go.scattermapbox.Marker(
                         size = 10,
                         color = color_list,
                         opacity = 0.8
                         ),
                showlegend = False
                
    ))

# Участок локализации разлива как полигон
figure.add_trace(go.Scattermapbox(
                lat=camp_geo[1],
                lon=camp_geo[0],
                mode='markers',
                fill='toself',
                name='Участок локализации разлива',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False
))

# Река Норильская как полигон
figure.add_trace(go.Scattermapbox(
                lat = norilskaya[1],
                lon = norilskaya[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Река Норильская',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

# приток реки Амбарная как полигон
figure.add_trace(go.Scattermapbox(
                lat = ambar2[1],
                lon = ambar2[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Приток реки Амбарная',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

# Река Далдыкан как полигон
figure.add_trace(go.Scattermapbox(
                lat = daldykan[1],
                lon = daldykan[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Река Далдыкан',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

# Река Амбарная как полигон
figure.add_trace(go.Scattermapbox(
                lat = ambar5[1],
                lon = ambar5[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Река Амбарная',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

figure.add_trace(go.Scattermapbox(
                lat = ambar4[1],
                lon = ambar4[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Приток реки Амбарная',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

# река Амбарная как полигон
figure.add_trace(go.Scattermapbox(
                lat = ambar3[1],
                lon = ambar3[0],
                mode = 'markers',
                fill = 'toself',
                name = 'река Амбарная',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False)
)

# Озеро Пясино как полигон
figure.add_trace(go.Scattermapbox(
                lat = pyasino[1],
                lon = pyasino[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Озеро Пясино',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False,
                hoverinfo = 'skip'
))

# Река Амбарная как полигон
figure.add_trace(go.Scattermapbox(
                lat = ambarnaya[1],
                lon = ambarnaya[0],
                mode = 'markers',
                fill = 'toself',
                name = 'Река Амбарная',
                marker = go.scattermapbox.Marker(
                         size = 1,
                         color = 'rgba(127, 219, 255, 0.4)'
                         ),
                showlegend = False,
                hoverinfo = 'skip'
))

# Верхний бон
figure.add_trace(go.Scattermapbox(
                lat = bon1[1],
                lon = bon1[0],
                mode = 'markers+lines',
                name = 'Верхний бон',
                marker = go.scattermapbox.Marker(
                         size = 12,
                         color = 'white'
                         ),
                showlegend = False
))

# Нижний бон
figure.add_trace(go.Scattermapbox(
                lat = bon2[1],
                lon = bon2[0],
                mode = 'markers+lines',
                name = 'Верхний бон',
                marker = go.scattermapbox.Marker(
                         size = 12,
                         color = 'white',
                         ),
                showlegend = False,
                hoverinfo = 'skip'
))

# Координаты Норильской ТЭЦ-3
figure.add_trace(go.Scattermapbox(lat = [69.321521],
                                  lon = [87.956233],
                                  name = 'Объекты',
                                  marker = go.scattermapbox.Marker(
                                                                   size = 12,
                                                                   color = 'red',
                                                                   opacity = 0.8,
                                                                   symbol = 'triangle'
                                                                   ),
                                  text = ['Норильская ТЭЦ-3'],
                                  mode = 'markers+text',
                                  showlegend = False
                                 ))

figure.update_traces(textposition = 'bottom center',
                     textfont = dict(family = "Verdana",
                                     size = 16,
                                     color = 'white'
    ))

figure.update_layout(
                  hovermode = 'closest',
                  hoverlabel = dict(
                                    bgcolor = 'black', 
                                    font_size = 12, 
                                    font_family = 'Verdana',
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
                  style = 'satellite',    
            
    )
)

app.layout = html.Div(html.Div(children = [
                                           html.H2('Мониторинг экологической обстановки',
                                                   style = {'color': 'darkgreen', 
                                                            'fontSize': 25,
                                                            'fontFamily' : 'Verdana',
                                                            'paddingLeft' : 80,
                                                            'paddingTop'  : 30
                                                           }
                                                  ),
                      
                                           html.Div(children = [ 
                                                                dcc.Graph(
                                                                          id = 'int_map', 
                                                                          figure = figure,
                                                                style = {'width' : '50%',
                                                                         'height' : 700,
                                                                         'paddingTop' : 0
                                                                         }
                                                                )]
                                                   ),
        
                                           html.Div(children = [dash_table.DataTable(
                                                                id = 'table',
                                                                columns = [{'name': i, 'id': i} for i in data_table.columns],
                                                                data = data_table.to_dict('records')
                                           )
                                                               ],
                                                    style = {'width' : '50%'}
                                                   )
]
                              )
)


if __name__ == '__main__':
    app.run_server(debug = True)

