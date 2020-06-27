#!/usr/bin/env python
# coding: utf-8

"""
    Вторая страница:
        - "Мониторинг отбора проб";
        - Карта с точками отборов проб;
        - Слайдер с анимацией по дням.
"""

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy  as np
import base64
import frontpage
import navigation_table
from dash.dependencies import Input, Output
from app import app

test = pd.read_csv('data//Разлив - Лист1.csv',
                    usecols = ['date', 'time_start', 'time_end', 'sampling_site', 'lon', 'lat', 'val', 'standard'])

test = test.replace(',', '.', regex = True)
test.iloc[:, 3:7] = test.iloc[:, 3:7].astype('float64')
test['excess'] = test.val / test.standard

test.loc[:, 'timestamp'] = pd.to_datetime(test.date, format = '%d.%m.%Y')

fict = [['29.05.2020', None, None, None, None, None, None, None, None, None],
        ['30.05.2020', None, None, None, None, None, None, None, None, None],
        ['31.05.2020', None, None, None, None, None, None, None, None, None]]

test_fict = pd.concat([pd.DataFrame(fict, columns = test.columns), test])

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

# Накопительным итогом
fig_map = px.scatter_mapbox(data_frame = test_fict,
                            lat = 'lat',
                            lon = 'lon',
                            animation_frame = 'date')

for i, date in enumerate(test.timestamp.unique()):
    anim_df = test[test.timestamp <= date]
    
    map_frames = fig_map['frames'][i + 3]['data'][0]
    
    map_frames['lat'] = anim_df.lat
    map_frames['lon'] = anim_df.lon
    map_frames['customdata'] = anim_df
    map_frames['hovertemplate'] = 'Результат отбора : %{customdata[5]:.2f} мг/дм3' + \
                                '<br>Превышение нормы в %{customdata[8]:.1f} раз</br>' +  \
                                '<br>Дата отбора : %{customdata[0]}' + \
                                '<br>Время начала отбора : %{customdata[1]}' + \
                                '<br>Время окончания отбора : %{customdata[2]}' + \
                                '<br>Место : %{customdata[7]}'
    map_frames['marker'] = go.scattermapbox.Marker(size = 14,
                                                   color = anim_df.excess)
    
map_marker = fig_map['data'][0]['marker']
map_marker['size'] = 14
map_marker['colorscale'] = ['#00a8ff', 'red']
map_marker['cmin'] = 0
map_marker['cmax'] = 5
map_marker['color'] = test.excess
    
fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 2000
fig_map.layout.sliders[0].pop('currentvalue')
fig_map.layout.sliders[0].active = 0

# Положение слайдера и его размеры
fig_map.layout.sliders[0].pad.t = 30
fig_map.layout.sliders[0].len = 0.90
fig_map.layout.sliders[0].x   = 0.07

# Цветовая гамма слайдера
fig_map.layout.sliders[0].currentvalue.visible = False
fig_map.layout.sliders[0].bordercolor = '#489e87'
fig_map.layout.sliders[0].borderwidth = 2
fig_map.layout.sliders[0].ticklen     = 4
fig_map.layout.sliders[0].bgcolor     = '#489e87'
fig_map.layout.sliders[0].font = {'family' : 'Helvetica',
                                  'size' : 16,
                                  'color' : '#489e87'}

# Положение кнопок
fig_map.layout.updatemenus[0].pad.r = 70
fig_map.layout.updatemenus[0].pad.t = 25
fig_map.layout.updatemenus[0].font = dict(color = '#3248a8')

fig_map.update_traces(marker_showscale = True)

# Параматры цветовой шкалы
map_marker.colorbar = dict(thickness = 10,
                           x = 0)

# Координаты Норильской ТЭЦ-3
fig_map.add_trace(go.Scattermapbox(lat = [69.321521],
                                  lon = [87.956233],
                                  name = 'Объекты',
                                  marker = go.scattermapbox.Marker(
                                                                   size = 12,
                                                                   color = 'blue',
                                                                   opacity = 0.8,
                                                                   symbol = 'triangle'
                                                                   ),
                                  text = ['Норильская ТЭЦ-3'],
                                  mode = 'markers+text',
                                  showlegend = False,
                                  hoverinfo = 'skip' 
                                 ))

fig_map.update_traces(textposition = 'bottom center',
                     textfont = dict(family = "Helvetica",
                                     size = 16,
                                     color = 'white'
    ))

fig_map.update_layout(
                  font = dict(color = 'white'),
                  coloraxis = dict(showscale = True),
                  margin = {'r' : 0,'t' : 0, 'l' : 0, 'b' : 0},
                  hovermode = 'closest',
                  hoverlabel = dict(
                                    bgcolor = 'black', 
                                    font_size = 14, 
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

# Хронологически
first_map = px.scatter_mapbox(data_frame = test_fict,
                              lat = 'lat',
                              lon = 'lon',
                              animation_frame = 'date')

for i, date in enumerate(test.timestamp.unique()):
    anim_df = test[test.timestamp == date]
    
    map_frames = first_map['frames'][i + 3]['data'][0]
    
    map_frames['lat'] = anim_df.lat
    map_frames['lon'] = anim_df.lon
    map_frames['customdata'] = anim_df
    map_frames['hovertemplate'] = 'Результат отбора : %{customdata[5]:.2f} мг/дм3' + \
                                '<br>Превышение нормы в %{customdata[8]:.1f} раз</br>' +  \
                                '<br>Дата отбора : %{customdata[0]}' + \
                                '<br>Время начала отбора : %{customdata[1]}' + \
                                '<br>Время окончания отбора : %{customdata[2]}' + \
                                '<br>Место : %{customdata[7]}'
    map_frames['marker'] = go.scattermapbox.Marker(size = 14,
                                                   color = anim_df.excess)
    
map_marker = first_map['data'][0]['marker']
map_marker['size'] = 14
map_marker['colorscale'] = ['#00a8ff', 'red']
map_marker['cmin'] = 0
map_marker['cmax'] = 5
map_marker['color'] = test.excess
    
first_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 2000
first_map.layout.sliders[0].pop('currentvalue')
first_map.layout.sliders[0].active = 0

# Положение слайдера и его размеры
first_map.layout.sliders[0].pad.t = 30
first_map.layout.sliders[0].len = 0.90
first_map.layout.sliders[0].x   = 0.07

# Цветовая гамма слайдера
first_map.layout.sliders[0].currentvalue.visible = False
first_map.layout.sliders[0].bordercolor = '#489e87'
first_map.layout.sliders[0].borderwidth = 2
first_map.layout.sliders[0].ticklen     = 4
first_map.layout.sliders[0].bgcolor     = '#489e87'
first_map.layout.sliders[0].font = {'family' : 'Helvetica',
                                  'size' : 16,
                                  'color' : '#489e87'}

# Положение кнопок
first_map.layout.updatemenus[0].pad.r = 70
first_map.layout.updatemenus[0].pad.t = 25
first_map.layout.updatemenus[0].font = dict(color = '#3248a8')

# Параматры цветовой шкалы
map_marker.colorbar = dict(thickness = 10,
                           x = 0)

# Координаты Норильской ТЭЦ-3
first_map.add_trace(go.Scattermapbox(lat = [69.321521],
                                  lon = [87.956233],
                                  name = 'Объекты',
                                  marker = go.scattermapbox.Marker(
                                                                   size = 12,
                                                                   color = 'blue',
                                                                   opacity = 0.8,
                                                                   symbol = 'triangle'
                                                                   ),
                                  text = ['Норильская ТЭЦ-3'],
                                  mode = 'markers+text',
                                  showlegend = False,
                                  hoverinfo = 'skip' 
                                 ))

first_map.update_traces(textposition = 'bottom center',
                        textfont = dict(family = "Helvetica",
                                     size = 16,
                                     color = 'white'
    ))

first_map.update_layout(
                font = dict(color = 'white'),
                margin = {'r' : 0,'t' : 0, 'l' : 0, 'b' : 0},
                hovermode = 'closest',
                hoverlabel = dict(
                                    bgcolor = 'black', 
                                    font_size = 14, 
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

tabs_styles = {
    'height'  : '40px',
    'width'   : '95%',
    'paddingLeft' : '20px',
    'paddingBottom' : '10px',
    'paddingTop' : '20px',
}

tab_style = {
    'borderBottom' : '1px solid #d6d6d6',
    'padding' : '6px',
    'fontFamily' : 'Helvetica',
    'fontSize' : 18,
    'verticalAlign' : 'middle',
    'borderRadius' : '20px',
    'color' : '#696969'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#489e87',
    'color': 'white',
    'padding': '6px',
    'fontFamily' : 'Helvetica',
    'fontSize' : 18,
    'verticalAlign' : 'middle',
    'borderRadius' : '30px'
}

def generate_graph():
    graph = html.Div([
    dcc.Tabs(id = 'tabs', 
            value = 'tab-1', 
            style = tabs_styles,
            children = [
        dcc.Tab(label = 'Хронологически', 
                value = 'tab-1',
                style = tab_style, 
                selected_style = tab_selected_style),
        dcc.Tab(label = 'Нарастающим итогом', 
                value = 'tab-2',
                style = tab_style,
                selected_style = tab_selected_style),
    ]),
    html.Div(id = 'basic_area')
])
    return graph

    
@app.callback(Output('basic_area', 'children'),
            [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(children = [
                                    dcc.Graph(
                                            id = 'int_map',
                                            figure = first_map,
                                            style = {'width' : '95%',
                                                    'height' : 600,
                                                    'paddingTop' : 20,
                                                    'paddingLeft': 20})]
                        )
    elif tab == 'tab-2':
        return html.Div(children = [
                                    dcc.Graph(
                                            id = 'int_map',
                                            figure = fig_map,
                                            style = {'width' : '95%',
                                                    'height' : 600,
                                                    'paddingTop' : 20,
                                                    'paddingLeft': 20}
                                            )
                                    ]
                        )

layout = html.Div([
    frontpage.generate_frontpage("Мониторинг отбора проб"),
    generate_graph(),
    navigation_table.table_link('/', '/norilsk2')
])
