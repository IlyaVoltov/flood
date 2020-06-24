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
    usecols=['date', 'time_start', 'time_end', 'val', 'standard' 'sampling_site'])
df = df.replace(',', '.', regex = True)
df['val'] = df['val'].astype('float64')
df['standard'] = df['standard'].astype('float64')
df['excess'] = df['val'] / df['standard']

column_names = [{"name": "Дата", "id": "date"},
                {"name": "Время начала отбора", "id": "time_start"},
                {"name": "Время окончания отбора", "id": "time_end"},
                {"name": "Номер пробы", "id": "number_of_samples"},
                {"name": "Кратность превышения", "id": "excess"},
                {"name": "Место отбора проб", "id": "sampling site"}
                ]

PAGE_SIZE = 20

measure_table = dash_table.DataTable(
    id='measure-table',
    columns=column_names,
    
    page_current=0,
    page_size=PAGE_SIZE,
    page_action='custom',

    sort_action='custom',
    sort_mode='single',
    sort_by=[]
)

layout = html.Div([
    frontpage.generate_frontpage("Данные по отбору проб"),
    measure_table
])

@app.callback(
    Output('measure-table', 'data'),
    [
        Input('measure-table', 'page_current'),
        Input('table-paging-and-sorting', 'page_size'),
        Input('table-paging-and-sorting', 'sort_by')
    ]
)
def update_table(page_current, page_size, sort_by):
    if len(sort_by):
        dff = df.sort_values(
            [col['column_id'] for col in sort_by],
            ascending=[
                col['direction'] == 'asc'
                for col in sort_by
            ],
            inplace=False
        )
    else:
        dff = df

    return dff.iloc[
        page_current * page_size:(page_current + 1) * page_size
    ].to_dict('records')