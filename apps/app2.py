#!/usr/bin/env python
# coding: utf-8

"""
    Вторая страница:
        - "Мониторинг отбора проб";
        - Карта с точками отборов проб;
        - Слайдер с анимацией по дням.
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy  as np
import base64
import frontpage
import navigation_table


first_june = pd.read_csv('data//Разлив - Лист1.csv',
                usecols = ['date', 'time_start', 'time_end','lon', 'lat', 'val', 'standard', 'sampling_site']) 

input_data = first_june.replace(',', '.', regex = True)
input_data['lon'] = input_data['lon'].astype('float64')
input_data['lat'] = input_data['lat'].astype('float64')
input_data['val'] = input_data['val'].astype('float64')
input_data['standard'] = input_data['standard'].astype('float64')
input_data['excess'] = round(input_data.val / input_data.standard, 1)

fict = [['29.05.2020', None, None, None, None, None, None, None, None],
        ['30.05.2020', None, None, None, None, None, None, None, None],
        ['31.05.2020', None, None, None, None, None, None, None, None]]

input_update = pd.DataFrame(fict, columns = input_data.columns)
in_data = pd.concat([input_update, input_data])

in_data.loc[:, 'timestamp'] = pd.to_datetime(in_data.date, format = '%d.%m.%Y')

agg_list = pd.DataFrame([], columns = in_data.columns)

for dt in in_data.timestamp.unique():
    dt_data = in_data[in_data.timestamp <= dt]
    i_date = in_data[in_data.timestamp.isin([dt])].date.index[0]
    dt_data.loc[:, 'date'] = in_data.iloc[i_date, 0]
    
    agg_list = pd.concat([agg_list, dt_data])

agg_list = agg_list[agg_list.date.isin(['29.05.2020']) == False]
eight = in_data[in_data.date.isin(['08.06.2020'])]
eight_agg = agg_list[agg_list.date == '07.06.2020']
eight_agg.loc[:, 'date'] = '08.06.2020'
eight_full = pd.concat([eight_agg, eight])

fict2 = [['29.05.2020', None, None, None, None, None, None, None, None, None]]
agg_list = pd.concat([pd.DataFrame(fict2, columns = agg_list.columns), agg_list])
agg_list = pd.concat([agg_list, eight_full])

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

fig_map = px.scatter_mapbox(
                            data_frame=agg_list,
                            lat='lat',
                            lon='lon',
                            animation_frame='date',
                            color_continuous_scale=px.colors.diverging.balance,
                            labels={
                                "date": "Дата отбора",
                                "excess": "Кратность превышения",
                                "sampling_site": "Место отбора"
                            },
                            hover_data={
                                "date":False,
                                "lat": False,
                                "lon": False,
                                "excess": ":.1f",
                                "sampling_site": True
                            },
                            color='excess',
                            range_color=[0, 10],
                            size=np.full((1, len(agg_list.index)), 5)[0])

fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 2500
fig_map.layout.sliders[0].pop('currentvalue')
fig_map.layout.sliders[0].active = 0

fig_map.layout.sliders[0].pad.t = 50
fig_map.layout.sliders[0].len = 0.90
fig_map.layout.sliders[0].x   = 0.07

fig_map.layout.sliders[0].currentvalue.visible = False
fig_map.layout.sliders[0].bordercolor = '#00a8ff'
fig_map.layout.sliders[0].borderwidth = 2
fig_map.layout.sliders[0].ticklen     = 4
fig_map.layout.sliders[0].bgcolor     = '#00a8ff'
fig_map.layout.sliders[0].font = {'family' : 'Helvetica',
                                  'size' : 18,
                                  'color' : '#00a8ff'}

fig_map.layout.updatemenus[0].pad.r = 60
fig_map.layout.updatemenus[0].pad.t = 40

fig_map.layout.coloraxis.colorbar = dict(
                                        thickness=10, 
                                        ticklen=3,
                                        tickcolor='rgb(255, 255, 255)',
                                        x=0)

fig_map.add_trace(go.Scattermapbox(
                                lat=[69.321521],
                                lon=[87.956233],
                                name='Объекты',
                                marker=go.scattermapbox.Marker(
                                                                size = 12,
                                                                color = 'blue',
                                                                opacity = 0.8,
                                                                symbol = 'triangle'
                                                            ),
                                text = ['Норильская ТЭЦ-3'],
                                textfont=dict(
                                        family="Helvetica",
                                        size=16,
                                        color="white"
                                ),
                                textposition='bottom center',
                                mode = 'markers+text',
                                showlegend = False
                                )
                )

fig_map.update_layout(
                  margin = {'r' : 0,'t' : 0, 'l' : 0, 'b' : 0},
                  hovermode = 'closest',
                  hoverlabel = dict(
                                    bgcolor = 'white', 
                                    font_size = 12, 
                                    font_family = 'Helvetica',
                                    font_color = 'black'
                                    ),
                  mapbox = dict(
                                accesstoken = access,
                                bearing = 0,
                                center = go.layout.mapbox.Center(
                                         lat = 69.444882, 
                                         lon = 87.915305
                                         ),
                  pitch=0,
                  zoom=8,   
                  style='satellite'   
    )
)

# for i, date in pd.Series(agg_list.date.unique()).iteritems():
#     date_stamp = 'Дата отбора - {}'.format(date)
#     excess = '<br>Кратность превышения - %{marker.color}</br>'
#     fig_map.frames[i].data[0].hovertemplate = date_stamp + excess


def generate_graph():
    graph = html.Div(children = [html.Div(children = [ dcc.Graph(
                                                                          id = 'int_map',
                                                                          figure = fig_map,
                                                                style = {'width' : '95%',
                                                                         'height' : '100%',
                                                                         'paddingTop' : 0,
                                                                         'paddingLeft': 15
                                                                         }
                                                                )]
                                                   )
                                    ])
    return graph

layout = html.Div([
    frontpage.generate_frontpage("Мониторинг отбора проб"),
    generate_graph(),
    navigation_table.table_link('/', '/norilsk2')
])
