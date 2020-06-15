import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy  as np
first_june = pd.read_csv('C:\\Users\\akimo\\OneDrive\\Desktop\\ИТ ФИЦ\\Разлив - Лист1.csv',
                         usecols = ['date', 'time_start', 'time_end','lon', 'lat', 'val', 'standard', 'cluster'])
input_data = first_june.replace(',', '.', regex = True)
input_data.iloc[:, 3:] = input_data.iloc[:, 3:].astype('float64')
input_data['excess'] = input_data.val / input_data.standard
access = 'pk.eyJ1Ijoia3Vrc2Vua29zcyIsImEiOiJjazE4NDlkZTQwMmtwM2NzenRmbm9rNjF2In0.j0d6QcToTviyQ0-KdzEIMA'
fig_map = px.scatter_mapbox(data_frame = input_data,
                            lat = 'lat',
                            lon = 'lon',
                            animation_frame = 'date',
                            color_continuous_scale = 'Bluered',
                            range_color = [0, 100],
                            color = 'excess')

fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
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
                                         lat = 69.495278,
                                         lon = 88.031250
                                         ),
                  pitch = 0,
                  zoom = 9.5,
                  style = 'satellite'
    )
)