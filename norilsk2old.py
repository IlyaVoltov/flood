#!/usr/bin/env python
# coding: utf-8

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy  as np
from   shapely.geometry import Polygon, Point
import json
import base64

def generate_frontpage(title):
    frontpage = html.Div(id='las-header', children=[
        html.A(
            html.Img(
                id='las-logo',
                src='data:image/png;base64,{}'.format(
                    base64.b64encode(
                        open('assets/rosprirodnadzor.png', 'rb').read()
                    ).decode()
                )), href='https://rpn.gov.ru/'),
        html.Div(
            id='las-header-text',
            children=[
                html.H1(title)]
                )
        ])

    return  frontpage

file = 'data//features.json'

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

first_june = pd.read_csv('data//Разлив - Лист1.csv',
                         usecols = ['date', 'time_start', 'time_end',
                                    'lon', 'lat', 'val', 'standard', 'cluster']) 

input_data = first_june.replace(',', '.', regex = True)
input_data.iloc[:, 3:] = input_data.iloc[:, 3:].astype('float64')
input_data['excess'] = input_data.val / input_data.standard

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
            geocode = comm_df.loc['coordinates', 'geometry']
            
        geo_lon = []
        geo_lat = []
        geo_cor = []
        
        for geo_inst in geocode:
            geo_lon.append(geo_inst[0]) 
            geo_lat.append(geo_inst[1])
            geo_cor.append(geo_inst)
        
        geo_array.append([poly_id, geo_lon, geo_lat, geo_cor])
            
    return geo_array

result_df = pd.DataFrame(poly_geo(file), columns = ['poly_id', 'lat', 'lon', 'coord'])                         \
    .set_index('poly_id')

poly_list = []
for poly_id, _, _, coord in result_df.itertuples():
    polygon = Polygon(coord)
    poly_list.append(polygon)
    
poly_array = pd.Series(poly_list, index = result_df.index)
    
point_list = []
for index, date, lat, lon in input_data[['date', 'lat', 'lon']].itertuples():
    point = Point([lon, lat])
    point_list.append(point)
    
point_array = pd.Series(point_list)

p_cluster = []
for i, point_item in point_array.iteritems():
    for j, poly_item in poly_array.iteritems():
        if poly_item.contains(point_item) == True:
            p_cluster.append([i, j])
            
cluster_df = pd.DataFrame(p_cluster, columns = ['point_id', 'polygon_id'])                          \
    .set_index('point_id')

res_df = pd.concat([input_data, cluster_df], axis = 1)

df_poly = []

for day in res_df.date.unique():
    res_by_day = res_df.groupby('date').get_group(day)
    
    res_by_day = res_by_day[res_by_day.polygon_id.isin([np.nan]) == False]
    
    for poly in res_by_day.polygon_id.unique():
        day_and_poly = res_by_day.groupby('polygon_id').get_group(poly)
        avg_excess = day_and_poly.excess.mean().round(1)
        
        df_poly.append([day, poly, avg_excess])

res = pd.DataFrame(df_poly, columns = ['date', 'polygon_id', 'avg_excess'])                   \
    .set_index('polygon_id')


df_day = res[res.date.isin(['05.06.2020'])]


fig_chor = go.Figure(go.Choroplethmapbox(geojson = jsondata, 
                                         locations = res.index,
                                         z = res.avg_excess,
                                         colorscale = ['#00a8ff', 'red'],
                                         
                                         colorbar = dict(thickness = 10, 
                                                         ticklen = 3,
                                                         x = -0.01),
                                         zmin = 0,
                                         zmax = 5,
                                         marker_line_width = 0))
fig_chor.update_layout(mapbox_style = "basic", 
                       mapbox_accesstoken = access,
                       mapbox_zoom = 7, 
                       mapbox_center = {'lat': 69.666084, "lon": 87.791365})

fig_chor.update_layout(margin = {"r" : 0, "t" : 0, "l" : 0, "b" : 0})


cm = px.choropleth_mapbox(data_frame = res,
                          geojson = jsondata,
                          locations = res.index,
                          color = res.avg_excess,
                          range_color = [0, 5],
                          color_continuous_scale = ['#00a8ff', 'red'],
                          animation_frame = 'date')


cm.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
cm.layout.sliders[0].pop('currentvalue')
cm.layout.sliders[0].active = 1

cm.layout.sliders[0].pad.t = 10
cm.layout.sliders[0].len = 0.90
cm.layout.sliders[0].x   = 0.07

cm.layout.sliders[0].bordercolor = '#00a8ff'
cm.layout.sliders[0].borderwidth = 2
cm.layout.sliders[0].ticklen     = 4
cm.layout.sliders[0].font = {'family' : 'Helvetica',
                                  'size' : 18,
                                  'color' : '#00a8ff'}

cm.layout.updatemenus[0].pad.r = 80
cm.layout.updatemenus[0].pad.t = 40

cm.layout.coloraxis.colorbar = dict(thickness = 10, 
                                         ticklen = 3,
                                         x = 0)

cm.layout.coloraxis.colorbar = dict(thickness = 10, 
                                    ticklen = 3,
                                    x = 0)

cm.update_layout(mapbox_style = "basic", 
                       mapbox_accesstoken = access,
                       mapbox_zoom = 8.9, 
                       mapbox_center = {'lat': 69.444882, "lon": 87.915305})

cm.update_layout(margin = {"r" : 0, "t" : 0, "l" : 0, "b" : 0})

def generate_graph():
    graph = html.Div(children = [
                                           html.Div(children = [
                                                                dcc.Graph(
                                                                          id = 'int_map',
                                                                          figure = cm,
                                                                style = {'width' : 900,
                                                                         'height' : 650,
                                                                         'paddingTop' : 0,
                                                                         'paddingLeft': 0
                                                                         }
                                                                )]
                                                   )
]
                              )
    return graph

norilsk2 = html.Div([
    generate_frontpage("Мониторинг секторов"),
    generate_graph()
])