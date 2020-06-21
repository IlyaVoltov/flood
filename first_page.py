#!/usr/bin/env python
# coding: utf-8

import dash
import dash_core_components as dcc
import dash_html_components as html
import norilsk
import norilsk2
import base64

app = dash.Dash(__name__)
server = app.server
app.css.config.serve_locally = True
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

def generate_frontpage(title):
    frontpage = html.Div(id='las-header', children=[
        html.A(
            html.Img(
                id='las-logo',
                src='data:image/png;base64,{}'.format(
                    base64.b64encode(
                        open('assets/rosprirodnadzor.png', 'rb').read()
                    ).decode()
                )), href='https://rpn.gov.ru/'),
        html.Div(
            id='las-header-text',
            children=[
                html.H1(title)]
                )
        ])

    return frontpage


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return start
    elif pathname == '/norilsk':
        return norilsk.norilsk
    elif pathname == '/norilsk2':
        return norilsk2.norilsk2
    else:
        return start

def create_barchart(poly_group):
    return {
        'data': [dict(
                    x=poly_group.date, type='bar',
                    y=poly_group.avg_excess,
                    marker_color='#00a8ff',
                    name='Показатели',
                    showlegend=False)],
               'layout': {
                   'yaxis_type': 'log',
                   'xaxis_title': 'Дата отбора воды',
                   'yaxis_title': 'Кратность превышения нормы на участке'}
            }


@app.callback(
    dash.dependencies.Output('bar_chart', 'figure'),
    [dash.dependencies.Input('map', 'hoverData')])
def create_plot(hover_data):
    res = norilsk2.res
    polygon_id = hover_data['points'][0]['location']
    polygon_group = res.groupby('polygon_id').get_group(polygon_id)

    return create_barchart(polygon_group)


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
            html.Td('!ДЕМО! Межрегиональное управление по   г. Москве и Калужской области'),
            html.Td('!ДЕМО! лесной пожар'),
            html.Td('!ДЕМО! 10 мая 2020 г'),
            html.Td(children=[
                html.Img(
                    id='alarm-logo',
                    src='data:image/jpg;base64,{}'.format(
                        base64.b64encode(open('assets/fire.PNG', 'rb').read()).decode())
                )
            ], className='table-line-three'),
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
    generate_frontpage('Авария'),
    table_link()
])

if __name__ == '__main__':
    app.run_server(debug=True)

