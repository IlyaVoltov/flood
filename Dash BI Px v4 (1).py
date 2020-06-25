#!/usr/bin/env python
# coding: utf-8
test = pd.read_csv('C:\\Users\ИТ ФИЦ\Desktop\BI Разлив\Разлив.csv',
                         usecols = ['date', 'time_start', 'time_end', 'sampling_site',
                                    'lon', 'lat', 'val', 'standard'])

test = test.replace(',', '.', regex = True)
test.iloc[:, 3:7] = test.iloc[:, 3:7].astype('float64')
test['excess'] = test.val / test.standard

test.loc[:, 'timestamp'] = pd.to_datetime(test.date, format = '%d.%m.%Y')

fict = [['29.05.2020', None, None, None, None, None, None, None, None, None],
        ['30.05.2020', None, None, None, None, None, None, None, None, None],
        ['31.05.2020', None, None, None, None, None, None, None, None, None]]

test_fict = pd.concat([pd.DataFrame(fict, columns = test.columns), test])

access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'

fig_map = px.scatter_mapbox(data_frame = test_fict,
                            lat = 'lat',
                            lon = 'lon',
                            animation_frame = 'date',
                            color_continuous_scale = ['#00a8ff', 'red'],
                            range_color = [0, 10])

for i, date in enumerate(test.timestamp.unique()):
    anim_df = test[test.timestamp <= date]
    
    map_frames = fig_map['frames'][i + 3]['data'][0]
    
    map_frames['lat'] = anim_df.lat
    map_frames['lon'] = anim_df.lon
    map_frames['customdata'] = anim_df
    map_frames['hovertemplate'] = 'Результат отбора : %{customdata[5]:.2f} мг/дм3' +                                 '<br>Превышение нормы в %{customdata[8]:.1f} раз</br>' +                                 '<br>Дата отбора : %{customdata[0]}' +                                 '<br>Время начала отбора : %{customdata[1]}' +                                 '<br>Время окончания отбора : %{customdata[2]}' +                                 '<br>Место : %{customdata[7]}'
    map_frames['marker'] = go.scattermapbox.Marker(size = 12,
                                                   color = anim_df.excess)
    
map_marker = fig_map['data'][0]['marker']
map_marker['size'] = 12
map_marker['colorscale'] = ['#00a8ff', 'red']
map_marker['cmin'] = 0
map_marker['cmax'] = 5
map_marker['color'] = test.excess
    
fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
fig_map.layout.sliders[0].pop('currentvalue')
fig_map.layout.sliders[0].active = 0

# Положение слайдера и его размеры
fig_map.layout.sliders[0].pad.t = 50
fig_map.layout.sliders[0].len = 0.90
fig_map.layout.sliders[0].x   = 0.07

# Цветовая гамма слайдера
fig_map.layout.sliders[0].currentvalue.visible = False
fig_map.layout.sliders[0].bordercolor = '#00a8ff'
fig_map.layout.sliders[0].borderwidth = 2
fig_map.layout.sliders[0].ticklen     = 4
fig_map.layout.sliders[0].bgcolor     = '#00a8ff'
fig_map.layout.sliders[0].font = {'family' : 'Helvetica',
                                  'size' : 18,
                                  'color' : '#00a8ff'}

# Положение кнопок
fig_map.layout.updatemenus[0].pad.r = 60
fig_map.layout.updatemenus[0].pad.t = 40

# Параматры цветовой шкалы
fig_map.layout.coloraxis.colorbar = dict(thickness = 10, 
                                         ticklen = 3,
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
                                     color = 'black'
    ))

fig_map.update_layout(
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
                  style = 'light'   
    )
)

app.layout = html.Div(html.Div(children = [
                                               
                                           html.Div(children = [ 
                                                                dcc.Graph(
                                                                          id = 'int_map', 
                                                                          figure = fig_map,
                                                                style = {'width' : '95%',
                                                                         'height' : '100%',
                                                                         'paddingTop' : 0,
                                                                         'paddingLeft': 15
                                                                         }
                                                                )]
                                                   )
]
                              )
)

