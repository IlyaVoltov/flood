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
            dcc.Link('Норильская ТЭЦ-3   ', href='/norilsk', id='link-1', className='tab first'),
            dcc.Link('Волховская ГЭС  ', href='/volhov', id='link-2', className='tab'),
            dcc.Link('Севро-Западная ТЭЦ  ', href='/northwest2', id='link-3', className='tab'),
        ], className='screen-top')

    return menu

def get_buttons():

    buttons = html.Div([

        html.Div([
            html.A([
                html.Img(
                    src=app.get_asset_url('norilsk.jpg'),
                    className='btn-img'
                ),
                html.H3('Норильская ТЭЦ-3'),
            ], href='/norilsk')
        ], className='grid-item'),

        html.Div([
            html.A([
                html.Img(
                    src=app.get_asset_url('volhov.jpg'),
                    className='btn-img'
            ),
            html.H3('Волховская ГЭС'),
             ], href='/volhov')
        ], className='grid-item'),

        html.Div([
                 html.A([
                    html.Img(
                    src=app.get_asset_url('northwest2.png'),
                    className='btn-img'
            ),
            html.H3('Северо-Западная ТЭЦ'),
            ], href='/northwest2')
            ], className = 'grid-item'),

    ], className='grid-container')

    return buttons

def generate_frontpage():
    frontpage = html.Div(id='las-header', children=[
            html.Img(
                id='las-logo',
                src='data:image/jpg;base64,{}'.format(
                    base64.b64encode(
                        open('assets/rosprirodnadzor.jpg', 'rb').read()
                    ).decode()
                )
            ),
            html.Img(
                id='logoftc',
                src='data:image/jpg;base64,{}'.format(
                    base64.b64encode(
                    open('assets/whodeploy.jpg', 'rb').read()
                ).decode()
            )),
            html.Div(
                id='las-header-text',
                children=[
                    html.H1("Система мониторинга экологической обстановки в РФ")]
            )
        ])

    return  frontpage

start = html.Div([
    generate_frontpage(),
    get_buttons()
])

if __name__ == '__main__':
    app.run_server(debug = True)