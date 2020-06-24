#!/usr/bin/env python
# coding: utf-8


"""
    Стартовая страница:
        - "Перечень аварий/чрезвычайных ситуаций";
        - Таблица со списком.
"""

import base64
import dash_core_components as dcc
import dash_html_components as html
import frontpage


def table_link():
    table = html.Div(id='table-objects', children=[
        html.Tr([
            html.Th('Территориальный орган'),
            html.Th('Место'),
            html.Th('Дата'),
            html.Th('Развитие событий')
        ], className='table-line-one'),
        html.Tr([
            html.Td('Енисейское межрегиональное управление'),
            html.Td('Норильская ТЭЦ-3 (АО "НТЭК")'),
            html.Td('29 мая 2020 г'),
            html.Td(children=[
                html.A(
                html.Img(
                    id='alarm-logo',
                    src='data:image/jpg;base64,{}'.format(
                        base64.b64encode(open('assets/alarm.png', 'rb').read()).decode())
                ), href='/norilsk')
            ]
            )], className='table-line-two')
    ])

    return table

layout = html.Div([
    frontpage.generate_frontpage('Перечень аварий/чрезвычайных ситуаций'),
    table_link()
])

