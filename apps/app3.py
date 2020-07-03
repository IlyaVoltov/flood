#!/usr/bin/env python
# coding: utf-8

"""
    Третья страница:
        - "Динамика ликвидации аварии";
        - карта с полигонами проб;
        - график с кратностью превышения по дням в этом полигоне.
"""

import dash
import time
import json
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from shapely.geometry import Polygon, Point
from dash.dependencies import Input, Output

import frontpage
import navigation_table
from app import app
from unix_time import unixTimeMillis, unixToDatetime

file = 'data//features.json'

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

test = pd.read_csv('data//flood.csv',
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
res['timestamp'] = pd.to_datetime(res['date'])
res['unix'] = res['timestamp'].apply(lambda x: unixTimeMillis(x))

p_list = []

for p in res.polygon_id.unique():
    poly_group = res.groupby('polygon_id').get_group(p)
    p_list.append(poly_group.iloc[-1, :])
    

@app.callback(
    Output('map', 'figure'),
    [
        Input('year-slider', 'value')
    ]
)
def update_map(date_picked):
    df = res[res['unix'] <= date_picked]
    cm = px.choropleth_mapbox(
                        data_frame=df,
                        geojson=jsondata,
                        locations='polygon_id',
                        color='avg_excess',
                        range_color=[0, 10],
                        color_continuous_scale=['#00a8ff', 'red'])

    cm.layout.coloraxis.colorbar = dict(
                                    thickness=10, 
                                    ticklen=3,
                                    tickcolor='white',
                                    x=0)
    cm['data'][0]['marker_line_width'] = 0

    # Координаты Норильской ТЭЦ-3
    cm.add_trace(go.Scattermapbox(
                                lat = [69.321521],
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
                    )
                )

    cm.update_layout(
                    mapbox_style='satellite', 
                    mapbox_accesstoken=access,
                    mapbox_zoom=7.3, 
                    mapbox_center={
                                    'lat': 69.444882, 
                                    'lon': 87.915305},
                    margin={
                                "r" : 15, "t" : 10, "l" : 0, "b" : 0}             
    )

    return cm


test['date'] = pd.to_datetime(test['date'], dayfirst=True)
test['date_only'] = test['date'].dt.date.astype('datetime64[ns]')

def getMarks():
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''
    result = {}
    for i, date in enumerate(test['date_only'].unique()):
        date = pd.to_datetime(date)
        if i % 3 == 1:
            result[unixTimeMillis(date)] = date.date()

    return result

def generate_graph():
    graph = html.Div([
        html.Div( 
            children = [
                html.Div([
                    dcc.Graph(id='map',
                        hoverData={
                            'points': [
                                {'location': '8c95756206039444095efcf05f77c9dc'}]})
        ], className='map-container'),
        dcc.Slider(
                id='year-slider',
                min = unixTimeMillis(test['date_only'].min()),
                max = unixTimeMillis(test['date_only'].max()),
                value = unixTimeMillis(test['date_only'].min()),
                marks=getMarks(),
                className='class-slider',
            ),
        get_weather_layout(),
        html.Div([
            dcc.Graph(id = 'bar_chart')
        ], className='bar-chart-container'),
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
    df['date'] = pd.to_datetime(df['dt_iso']).apply(lambda x: x.date())
    df['unix'] = df['date'].apply(lambda x: unixTimeMillis(x))
    df = df.set_index('dt_iso')
    df = df.fillna(0)
    idx = None
    for i, unix in enumerate(df['unix'].unique()):
        if unix == picked_date:
            idx = i
    if i is not None:
        match = df.iloc[idx]
    else:
        match = None       

    return match

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
            html.Table([
                html.Tr([
                    html.Th('Температура воздуха, °C'),
                    html.Th('Скорость ветра, м/c'),
                    html.Th('Выпало дождя, мм'),
                    html.Th('Направление ветра')
                ], className='weather-table-header'),
                html.Tr([
                    html.Td(id='temp-value'),
                    html.Td(id='wind-value'),
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
        Input('year-slider', 'value')
    ]
)
def get_weather_data(date_slider):
    df = get_weather_archive('data//weather_archive.csv', date_slider)
    if df is not None:
        icon_path = get_wind_direction(df['wind_deg'])
        wind_speed = df['wind_speed']
        temperature = df['temp']
        rainfall = df['rain_3h']
    else:
        icon_path = get_wind_direction(0)
        wind_speed = 'no results'
        temperature = 'no results'
        rainfall = 'no results'
    return ([
        temperature,
        rainfall,
        wind_speed,
        app.get_asset_url(icon_path),
    ])

layout = html.Div([
    frontpage.generate_frontpage("Динамика ликвидации аварии"),
    generate_graph(),
    navigation_table.table_link('/norilsk', '/norilsk/table'),
])
