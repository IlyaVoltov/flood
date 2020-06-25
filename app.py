#!/usr/bin/env python
# coding: utf-8

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

if __name__ == '__main__':
    app.run_server(host='0.0.0.0')
