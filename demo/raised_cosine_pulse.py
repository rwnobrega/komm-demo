import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div([
        html.Div([
            html.P(
                id=uid('rolloff-label'),
            ),
            dcc.Slider(
                id=uid('rolloff-slider'),
                min=0,
                max=1,
                value=0.5,
                step=0.01,
            )],
            style={'margin-bottom': '24px'},
        )],
        style={'vertical-align': 'top'},
    ),

    html.Div(
        id=uid('graphs'),
    ),
])

# ---

import komm
import numpy as np

@app.callback(
    dash.dependencies.Output(component_id=uid('rolloff-label'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('rolloff-slider'), component_property='value')]
)
def _(rolloff):
    return 'Rolloff: {:.2f}'.format(rolloff)

@app.callback(
    dash.dependencies.Output(component_id=uid('graphs'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('rolloff-slider'), component_property='value')]
)
def raised_cosine_update(rolloff):
    pulse = komm.RaisedCosinePulse(rolloff, length_in_symbols=20)
    h = pulse.impulse_response
    H = pulse.frequency_response
    t = np.linspace(-8.0, 8.0, 800)
    f = np.linspace(-1.5, 1.5, 150)

    figure_impulse_response = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=t,
                    y=h(t),
                    mode='lines',
                    line=dict(
                        color='blue',
                    ),
                ),
            ],
            layout=go.Layout(
                title='Raised cosine pulse (waveform)',
                xaxis=dict(
                    title='t',
                    range=[-7.1, 7.1],
                ),
                yaxis=dict(
                    title='h(t)',
                    range=[-0.25, 1.25],
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'width': '50%', 'height': '400', 'display': 'inline-block'},
        id=uid('impulse-response-figure'),
    )

    figure_frequency_response = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=f,
                    y=H(f),
                    mode='lines',
                    line=dict(
                        color='red',
                    ),
                ),
            ],
            layout=go.Layout(
                title='Raised cosine pulse (spectrum)',
                xaxis=dict(
                    title='f',
                    range=[-1.5, 1.5],
                ),
                yaxis=dict(
                    title='H(f)',
                    range=[-0.25, 1.25],
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'width': '50%', 'height': '400', 'display': 'inline-block'},
        id=uid('frequency-response-figure'),
    )
    return [figure_impulse_response, figure_frequency_response]
