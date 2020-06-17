#!/usr/bin/env python
# coding: utf-8

import dash
import dash_core_components as dcc
import dash_html_components as html
from norilsk import norilsk

app = dash.Dash(__name__)
server = app.server

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
    '''
    elif pathname == '/volhov':
        return volhov
    elif pathname == '/northwest':
        return northwest
    '''

def get_menu():

    menu = html.Div([
            dcc.Link('Норильская ТЭЦ-3   ', href='/norilsk', id='link-1', className='tab first'),
            dcc.Link('Волховская ГЭС  ', href='/volhov', id='link-2', className='tab'),
            dcc.Link('Севро-Западная ТЭЦ  ', href='/northwest', id='link-3', className='tab'),
        ], className='screen-top')

    return menu

def header():
    return html.Div([
        html.Div([
            html.H2("Система мониторига аварийных ситуаций")
        ]),
    ], className='header')

start = html.Div([
        header(),
        get_menu(),
        html.Div([
            html.H1("That's a placeholder")
        ])
    ])

if __name__ == '__main__':
    app.run_server(debug = True)