#!/usr/bin/env python
# coding: utf-8

import dash
import os
import base64
import dash_core_components as dcc
import dash_html_components as html
from norilsk import norilsk

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return start
    elif pathname == '/norilsk':
        return norilsk
    else:
        return start

def get_menu():

    menu = html.Div([
            dcc.Link('Норильская ТЭЦ-3', href='/norilsk', id='link-1', className='tab first'),
            dcc.Link('сайт РПН', href='https://rpn.gov.ru/', id='link-2', className='tab'),
        ], className='screen-top')

    return menu

def generate_frontpage():
    frontpage = html.Div(id='las-header', children=[
        html.A(
            html.Img(
                id='las-logo',
                src='data:image/jpg;base64,{}'.format(
                    base64.b64encode(
                        open('assets/rosprirodnadzor.png', 'rb').read()
                    ).decode()
                )), href='https://rpn.gov.ru/'),
        html.Div(
            id='las-header-text',
            children=[
                html.H1("Аварии")]
                )
        ])

    return  frontpage

def table_link():
    table = html.Div([
        html.Tr([
            html.Th('Территориальный орган'),
            html.Th('Место'),
            html.Th('Дата'),
            html.Th('Развитие событий')
        ], className='table-line-one'),
        html.Tr([
            html.Td('Южно-Сибирское межрегиональное управление'),
            html.Td('Норильская ТЭЦ-3'),
            html.Td('29 мая 2020 г'),
            html.Td(children=[
                html.A(
                html.Img(
                    id='alarm-logo',
                    src='data:image/jpg;base64,{}'.format(
                        base64.b64encode(open('assets/alarm.png', 'rb').read()).decode())
                ), href='/norilsk')
            ]
            )], className='table-line-two'),
        html.Tr([
            html.Td('!ДЕМО! Межрегиональное управление по   г. Москве и Колужской области'),
            html.Td('!ДЕМО! лесной пожар'),
            html.Td('!ДЕМО! 10 мая 2020 г'),
            html.Td(children=[
                html.Img(
                    id='alarm-logo',
                    src='data:image/jpg;base64,{}'.format(
                        base64.b64encode(open('assets/fire.PNG', 'rb').read()).decode())
                )
            ], className = 'table-line-three'),
        ]),
        html.Tr([
            html.Td('!ДЕМО! Межрегиональное управление по Ростовской области и Республике Калмыкия'),
            html.Td('!ДЕМО! паводок'),
            html.Td('!ДЕМО! 1 апреля 2020 г'),
            html.Td(children=[
                html.Img(
                        id='alarm-logo',
                        src='data:image/jpg;base64,{}'.format(
                            base64.b64encode(open('assets/water.jpg', 'rb').read()).decode())
                    )
                ], className='table-line-four')
        ])
    ])

    return table

start = html.Div([
    generate_frontpage(),
    table_link()
])

if __name__ == '__main__':
    app.run_server(debug = True)