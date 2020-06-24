from app import app
import dash_html_components as html


def generate_frontpage(title):
    return(
            html.Div([
                html.Div(id='las-header', children=[
                    html.Div(
                        id='logo',
                        children=[
                            
                            html.A(
                                html.Img(
                                    id='logo-image',
                                    src=app.get_asset_url('logo.svg'),
                                ), href='https://rpn.gov.ru/'
                            ),
                            html.Div(
                                id='logo-info',
                                children=[
                                        html.P("Росприроднадзор", id='logo-title'),
                                        html.P("Федеральная служба по надзору в сфере природопользования", id='logo-subtitle')
                                ]
                            )
                        ]
                    ),
                    html.P(
                        "Интерактивная система мониторинга экологической обстановки на территории Российской Федерации",
                        id='system-name'
                    )
                ]),
                html.Div(
                    id='las-header-text',
                    children=[
                        html.H2(title)]
                )
            ])
        )