#!/usr/bin/env python
# coding: utf-8

"""
    Четвертая страница;
        - "Данные по отбору проб";
        - Таблица с данными:
            - Дата и время отбора;
            - Номер забора;
            - Забор;
            - Место
"""

import dash_table
import frontpage
import pandas as pd
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

df = pd.read_csv('data//Разлив - Лист1.csv', 
    usecols=['date', 'time_start', 'time_end', 'number_of_samples', 'val', 'standard', 'sampling_site'])
df = df.replace(',', '.', regex = True)
df['val'] = df['val'].astype('float64')
df['standard'] = df['standard'].astype('float64')
df['excess'] = round(df['val'] / df['standard'], 2)

column_names = [{"name": "Дата", "id": "date"},
                {"name": "Время начала отбора", "id": "time_start"},
                {"name": "Время окончания отбора", "id": "time_end"},
                {"name": "Номер пробы", "id": "number_of_samples"},
                {"name": "Кратность превышения", "id": "excess"},
                {"name": "Место отбора проб", "id": "sampling_site"}
                ]

PAGE_SIZE = 10

def generate_table():
    measure_table = dash_table.DataTable(
        id='datatable-paging',
        columns=column_names,
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom',
        style_cell={
            'textAlign': 'left',
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '15px'
        },
        style_header={
            'backgroundColor': 'rgb(108, 117, 111)',
            'fontWeight': 'bold'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'date'},
            'width': '15%'},
            {'if': {'column_id': 'excess'},
            'width': '20%'},
        ]
    )

    return measure_table

layout = html.Div([
    frontpage.generate_frontpage("Данные по отбору проб"),
    generate_table()
])


@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size")])
def update_table(page_current,page_size):
    return df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')