#!/usr/bin/env python
# coding: utf-8

import dash
import dash_core_components as dcc
import dash_html_components as html
import base64
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from shapely.geometry import Polygon, Point
import json
import frontpage

from app import app

file = 'data//features.json'

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

first_june = pd.read_csv('data//Разлив - Лист1.csv',
                         usecols=['date', 'time_start', 'time_end',
                                  'lon', 'lat', 'val', 'standard', 'cluster'])

input_data = first_june.replace(',', '.', regex=True)
input_data.iloc[:, 3:] = input_data.iloc[:, 3:].astype('float64')
input_data['excess'] = input_data.val / input_data.standard

openfile = open(file)
jsondata = json.load(openfile)
df = pd.DataFrame(jsondata)
openfile.close()


def table_link():
    table = html.Div(
       children=[
                html.A(
                    html.Img(
                        id='back',
                        src='data:image/JPG;base64,{}'.format(
                            base64.b64encode(open('assets/back.JPG', 'rb').read()).decode())
                    ), href='/norilsk')
])

    return table

def poly_geo(file_path):
    openfile = open(file_path)
    jsondata = json.load(openfile)
    df = pd.DataFrame(jsondata)
    openfile.close()

    geo_array = []

    for i, feat, _ in df.itertuples():
        poly_id = feat['id']
        comm_df = pd.DataFrame(feat)
        f_type = comm_df.loc['type', 'geometry']

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

result_df = pd.DataFrame(poly_geo(file), columns=['poly_id', 'lat', 'lon', 'coord']).set_index('poly_id')

poly_list = []
for poly_id, _, _, coord in result_df.itertuples():
    polygon = Polygon(coord)
    poly_list.append(polygon)

poly_array = pd.Series(poly_list, index=result_df.index)

point_list = []
for index, date, lat, lon in input_data[['date', 'lat', 'lon']].itertuples():
    point = Point([lon, lat])
    point_list.append(point)

point_array = pd.Series(point_list)

p_cluster = []
for i, point_item in point_array.iteritems():
    for j, poly_item in poly_array.iteritems():
        if poly_item.contains(point_item):
            p_cluster.append([i, j])

cluster_df = pd.DataFrame(p_cluster, columns=['point_id', 'polygon_id']).set_index('point_id')

res_df = pd.concat([input_data, cluster_df], axis=1)

df_poly = []

for day in res_df.date.unique():
    res_by_day = res_df.groupby('date').get_group(day)

    res_by_day = res_by_day[res_by_day.polygon_id.isin([np.nan]) == False]

    for poly in res_by_day.polygon_id.unique():
        day_and_poly = res_by_day.groupby('polygon_id').get_group(poly)
        avg_excess = day_and_poly.excess.mean().round(1)

        df_poly.append([day, poly, avg_excess])

res = pd.DataFrame(df_poly, columns=['date', 'polygon_id', 'avg_excess'])

p_list = []

for p in res.polygon_id.unique():
    poly_group = res.groupby('polygon_id').get_group(p)
    p_list.append(poly_group.iloc[-1, :])

df_map = pd.DataFrame(p_list)

pmap = go.Figure(go.Choroplethmapbox(geojson = jsondata,
                                     locations = df_map.polygon_id,
                                     z = df_map.avg_excess,
                                     zmin = 0,
                                     zmax = 5,
                                     colorscale = ['#00a8ff', 'red'],
                                     colorbar = dict(thickness = 10, 
                                                     ticklen = 3,
                                                     x = 0),
                                     customdata = df_map,
                                     hovertemplate = 'Превышение нормы в %{customdata[2]:.1f} раз',
                                     name = 'Отборы воды',
                                     marker_line_width = 0))

pmap.add_trace(go.Scattermapbox(lat = [69.321521],
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
                                                  color = 'black'),
                                  mode = 'markers+text',
                                  showlegend = False
                                 ))

pmap.update_layout(
                  margin = {'r' : 0,'t' : 0, 'l' : 0, 'b' : 0},
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
                                         lat = 69.444882, 
                                         lon = 87.915305
                                         ),
                  pitch = 0,
                  zoom = 8,   
                  style = 'satellite'   
    )
)

def generate_graph():
    graph = html.Div([
        html.Div(id='page',children=[
            dcc.Graph(
                        id='map',
                        figure=pmap,
                        hoverData={
                          'points': [
                              {'location': '8c95756206039444095efcf05f77c9dc'}
                          ]}
            ),
            html.Div([
                dcc.Graph(id='bar_chart')
        ])
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
                    showlegend = False),
                dict(
                    x = poly_group.date,
                    y = poly_group.avg_excess,
                    type = 'scatter',
                    marker = dict(color = 'red'),
                    name = 'Тренд',
                    showlegend = False)],
        
        'layout': dict(
                   yaxis = dict(type = 'log', 
                                title = 'Кратность превышения нормы на участке'),
                   title = 'Динамика развития аварии',
                   xaxis = dict(title = 'Дата отбора воды'))}


@app.callback(
    dash.dependencies.Output('bar_chart', 'figure'),
    [dash.dependencies.Input('map', 'hoverData')])
def create_plot(hover_data):
    polygon_id = hover_data['points'][0]['location']
    polygon_group = res.groupby('polygon_id').get_group(polygon_id)

    return create_barchart(polygon_group)

layout = html.Div([
    frontpage.generate_frontpage("Динамика ликвидации аварии"),
    generate_graph(),
    table_link()
])
