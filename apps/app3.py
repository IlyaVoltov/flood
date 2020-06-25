#!/usr/bin/env python
# coding: utf-8

"""
    Третья страница:
        - "Динамика ликвидации аварии";
        - карта с полигонами проб;
        - график с кратностью превышения по дням в этом полигоне.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import json
from datetime import datetime as dt
from dash.dependencies import Input, Output

import frontpage
import navigation_table
from app import app

file = 'data//features.json'

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

test = pd.read_csv('data//Разлив - Лист1.csv',
                        usecols = ['date', 'time_start', 'time_end', 'sampling_site', 'lon', 'lat', 'val', 'standard'])

test = test.replace(',', '.', regex = True)
test.iloc[:, 3:7] = test.iloc[:, 3:7].astype('float64')
test['excess'] = test.val / test.standard

test.loc[:, 'timestamp'] = pd.to_datetime(test.date, format = '%d.%m.%Y')

openfile = open(file)
jsondata = json.load(openfile)
df = pd.DataFrame(jsondata)
openfile.close()

def poly_geo(file_path):
    openfile = open(file_path)
    jsondata = json.load(openfile)
    df = pd.DataFrame(jsondata)
    openfile.close()
    
    geo_array = []
    
    for i, feat, _ in df.itertuples():
        poly_id = feat['id']
        comm_df = pd.DataFrame(feat)
        f_type  = comm_df.loc['type', 'geometry']
        
        if f_type == 'Polygon':
            geocode = comm_df.loc['coordinates', 'geometry'][0]
        else:
            continue
            
        geo_lon = []
        geo_lat = []
        geo_cor = []
        
        for geo_inst in geocode:
            geo_lon.append(geo_inst[0]) 
            geo_lat.append(geo_inst[1])
            geo_cor.append(geo_inst)
        
        geo_array.append([poly_id, geo_lon, geo_lat, geo_cor])
            
    return geo_array

result_df = pd.DataFrame(poly_geo(file), columns = ['poly_id', 'lat', 'lon', 'coord']).set_index('poly_id')

poly_list = []
for poly_id, _, _, coord in result_df.itertuples():
    polygon = Polygon(coord)
    poly_list.append(polygon)
    
poly_array = pd.Series(poly_list, index = result_df.index)
    
point_list = []
for index, date, lat, lon in test[['date', 'lat', 'lon']].itertuples():
    point = Point([lon, lat])
    point_list.append(point)
    
point_array = pd.Series(point_list)

p_cluster = []
for i, point_item in point_array.iteritems():
    for j, poly_item in poly_array.iteritems():
        if poly_item.contains(point_item) == True:
            p_cluster.append([i, j])
            
cluster_df = pd.DataFrame(p_cluster, columns = ['point_id', 'polygon_id']).set_index('point_id')


res_df = test.join(cluster_df)
df_poly = []

for day in res_df.date.unique():
    res_by_day = res_df.groupby('date').get_group(day)
    
    res_by_day = res_by_day[res_by_day.polygon_id.isin([np.nan]) == False]
    
    for poly in res_by_day.polygon_id.unique():
        day_and_poly = res_by_day.groupby('polygon_id').get_group(poly)
        avg_excess = day_and_poly.excess.mean().round(1)
        
        df_poly.append([day, poly, avg_excess])

res = pd.DataFrame(df_poly, columns = ['date', 'polygon_id', 'avg_excess'])

p_list = []

for p in res.polygon_id.unique():
    poly_group = res.groupby('polygon_id').get_group(p)
    p_list.append(poly_group.iloc[-1, :])
    

cm = px.choropleth_mapbox(
                        data_frame=res,
                        geojson=jsondata,
                        locations='polygon_id',
                        color='avg_excess',
                        animation_frame='date',
                        range_color=[0, 10],
                        color_continuous_scale=['#00a8ff', 'red'])

cm.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 2500
cm.layout.sliders[0].pop('currentvalue')
cm.layout.sliders[0].active = 0

# Положение слайдера и его размеры
cm.layout.sliders[0].pad.t = 50
cm.layout.sliders[0].len = 0.90
cm.layout.sliders[0].x   = 0.07

# Цветовая гамма слайдера
cm.layout.sliders[0].currentvalue.visible = False
cm.layout.sliders[0].bordercolor = '#3248a8'
cm.layout.sliders[0].borderwidth = 2
cm.layout.sliders[0].ticklen     = 4
cm.layout.sliders[0].bgcolor     = '#3248a8'
cm.layout.sliders[0].font = {'family' : 'Helvetica',
                             'size' : 14,
                             'color' : '#3248a8'}

# Положение кнопок
cm.layout.updatemenus[0].pad.r = 60
cm.layout.updatemenus[0].pad.t = 40

# Параматры цветовой шкалы
cm.layout.coloraxis.colorbar = dict(thickness = 10, 
                                    ticklen = 3,
                                    tickcolor = 'white',
                                    x = 0)
cm['data'][0]['marker_line_width'] = 0

# Координаты Норильской ТЭЦ-3
cm.add_trace(go.Scattermapbox(lat = [69.321521],
                                  lon = [87.956233],
                                  name = 'Объекты',
                                  marker = go.scattermapbox.Marker(
                                                                   size = 12,
                                                                   color = 'blue',
                                                                   opacity = 0.8,
                                                                   symbol = 'triangle'
                                                                   ),
                                  text = 'Норильская ТЭЦ-3',
                                  textposition = 'bottom center',
                                  textfont = dict(family = "Helvetica",
                                                  size = 14,
                                                  color = 'white'),
                                  mode = 'markers+text',
                                  showlegend = False,
                                  hoverinfo = 'skip'
                                 ))

cm.update_layout(mapbox_style = 'satellite', 
                 mapbox_accesstoken = access,
                 mapbox_zoom = 7.3, 
                 mapbox_center = {'lat': 69.444882, 
                                    'lon': 87.915305})

cm.update_layout(margin = {"r" : 15, "t" : 10, "l" : 0, "b" : 0})


def generate_graph():
    graph = html.Div([
        html.Div( 
            children = [
                html.Div([
                    dcc.Graph(id = 'map', 
                        figure = cm,
                        hoverData = {
                            'points': [
                                {'location': '8c95756206039444095efcf05f77c9dc'}]})
        ]),
        html.Div([
            dcc.Graph(id = 'bar_chart')
        ]),
    ])
])

    return graph


def create_barchart(poly_group):
    return {
        'data': [dict(
                    x = poly_group.date,
                    y = poly_group.avg_excess,
                    type = 'bar',
                    marker = dict(color = '#00a8ff'),
                    name = 'Показатели',
                    text = poly_group.avg_excess.round(1),
                    textposition = 'outside',
                    showlegend = False)],
        
        'layout': dict(
                yaxis = dict(
                            type = 'log', 
                            title = 'Кратность превышения нормы на участке'),
                xaxis = dict(
                            title = 'Дата отбора воды'))
        }


@app.callback(
    dash.dependencies.Output('bar_chart', 'figure'),
    [dash.dependencies.Input('map', 'hoverData')])
def create_plot(hover_data):
    polygon_id = hover_data['points'][0]['location']
    polygon_group = res.groupby('polygon_id').get_group(polygon_id)

    return create_barchart(polygon_group)


def get_weather_archive(filename, picked_date):
    df = pd.read_csv(
        filename, 
        usecols=['dt_iso', 'temp', 'wind_speed', 'wind_deg', 'rain_3h', 'snow_3h'])
    df['dt_iso'] = pd.to_datetime(df['dt_iso'])
    df['date'] = pd.to_datetime(df['dt_iso'].apply(lambda x: x.date()))
    df = df.set_index('dt_iso')
    df = df.fillna(0)

    return df[df['date'] == picked_date]

def get_wind_direction(wind_degrees):
    if wind_degrees > 23 and wind_degrees <= 67:
        direction = 'NE'
    elif wind_degrees > 67 and wind_degrees <= 112:
        direction = 'E'
    elif wind_degrees > 112 and wind_degrees <= 156:
        direction = 'SE'
    elif wind_degrees > 156 and wind_degrees <= 200:
        direction = 'S'
    elif wind_degrees > 200 and wind_degrees <= 244:
        direction = 'SW'
    elif wind_degrees > 244 and wind_degrees <= 288:
        direction = 'W'
    elif wind_degrees > 288 and wind_degrees < 333:
        direction = 'NW'
    else: 
        direction = 'N'
    icon_path = direction + '.gif'

    return icon_path

def get_weather_layout():
    layout = html.Div([
            html.Div([
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=dt(2020, 5, 29),
                    max_date_allowed=dt(2020, 6, 21),
                    date=dt(2020, 5, 29)
                )
            ]),
            html.Table([
                html.Tr([
                    html.Th('Температура воздуха, °C'),
                    html.Th('Скорость ветра, м/c'),
                    html.Th('Выпало дождя, мм'),
                    html.Th('Направление ветра')
                ], className='weather-table-header'),
                html.Tr([
                    html.Td(id='wind-value'),
                    html.Td(id='temp-value'),
                    html.Td(id='rainfall-value'),
                    html.Img(id='wind-icon')
                ], className='weather-table-row')
            ], id='weather-table')
        ], className='weather-container')

    return layout


@app.callback(
    [
        Output('temp-value', 'children'),
        Output('rainfall-value', 'children'),
        Output('wind-value', 'children'),
        Output('wind-icon', 'src')
    ],
    [
        Input('my-date-picker-single', 'date')
    ]
)
def get_weather_data(date):
    df = get_weather_archive('data//weather_archive.csv', date)
    icon_path = get_wind_direction(df['wind_deg'].values[0])
    wind_speed = df['wind_speed'].values[0]
    temperature = df['temp'].values[0]
    rainfall = df['rain_3h'].values[0]
    snowfall = df['snow_3h'].values[0]
    return ([
        temperature,
        rainfall,
        wind_speed,
        app.get_asset_url(icon_path),
    ])

layout = html.Div([
    frontpage.generate_frontpage("Динамика ликвидации аварии"),
    generate_graph(),
    get_weather_layout(),
    navigation_table.table_link('/norilsk', '/norilsk/table'),
])
