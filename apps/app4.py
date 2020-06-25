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
import navigation_table
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

PAGE_SIZE = 7

def generate_table():
    measure_table = dash_table.DataTable(
        id='datatable-paging',
        columns=column_names,
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom',
        style_data={
            'textAlign': 'central',
            'whiteSpace': 'normal',
	    'height': 'auto',
        },
        css=[{
            'selector': '.dash-spreadsheet td div',
            'rule': '''
                line-height: 15px;
                max-height: 45px; min-height: 45px; height: 45px;
                display: block;
                overflow-y: hidden;
            '''
        }],
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df.to_dict('rows')
        ],
        tooltip_duration=None,
        style_header={
            'backgroundColor': 'rgb(108, 117, 111)',
            'fontWeight': 'bold'
        },
        style_cell_conditional=[
            {
                'if': {
                    'filter_query': '{excess} > 100',
                },
                'backgroundColor': 'rgb(221, 127, 95)'
            }
        ]
    )

    return measure_table

layout = html.Div([
    frontpage.generate_frontpage("Данные по отбору проб"),
    generate_table(),
    navigation_table.table_link('/norilsk2', '/')
])


@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', "page_current"),
     Input('datatable-paging', "page_size")])
def update_table(page_current,page_size):
    return df.iloc[
        page_current*page_size:(page_current+ 1)*page_size
    ].to_dict('records')
