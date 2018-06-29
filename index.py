import importlib
import json

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

with open('app_menu.json') as f:
    app_menu = json.load(f)

menu_layout_div = [html.H2('Menu')]

for app_id, app_dict in app_menu.items():
    app_dict['dash_layout'] = importlib.import_module('demo.' + app_id).layout
    menu_layout_div.append(html.A(app_dict['menu_name'], href='/' + app_id))
    menu_layout_div.append(html.Br())

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.H1('Komm demo', style={'text-align': 'center'}),
    html.Div([
        html.Div(menu_layout_div, className='two columns', style={'width': '13%'}),
        html.Div(id='page-content', className='two columns', style={'width': '82%'}),
    ]),
], style={'width': '90%', 'margin': 'auto'})


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return
    elif pathname == '/':
        return 'Welcome!'
    elif pathname.startswith('/'):
        app_id = pathname[1:]
        if app_id in app_menu:
            app_dict = app_menu[app_id]
            return html.Div([
                html.H2(app_dict['title']),
                html.P(['Documentation reference: ', html.A(app_dict['doc'], href=app_dict['doc'])]),
                app_dict['dash_layout'],
            ])

    return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
