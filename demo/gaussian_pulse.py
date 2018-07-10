import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div([
        html.Div([
            html.P(
                id=uid('half-power-bandwidth-label'),
            ),
            dcc.Slider(
                id=uid('half-power-bandwidth-slider'),
                min=0.05,
                max=1.0,
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
    Output(component_id=uid('half-power-bandwidth-label'), component_property='children'),
    [Input(component_id=uid('half-power-bandwidth-slider'), component_property='value')]
)
def _(half_power_bandwidth):
    return 'Half-power bandwidth: {:.2f}'.format(half_power_bandwidth)

@app.callback(
    Output(component_id=uid('graphs'), component_property='children'),
    [Input(component_id=uid('half-power-bandwidth-slider'), component_property='value')]
)
def gaussian_pulse_update(half_power_bandwidth):
    Bh = half_power_bandwidth
    pulse = komm.GaussianPulse(Bh, length_in_symbols=4)
    h = pulse.impulse_response
    H = pulse.frequency_response
    t = np.linspace(-8.0, 8.0, 1000)
    f = np.linspace(-4.0, 4.0, 500)

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
                title='Gaussian pulse (waveform)',
                xaxis=dict(
                    title='t',
                    range=[-7.1, 7.1],
                ),
                yaxis=dict(
                    title='h(t)',
                    range=[-0.1, 1.1],
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
                go.Scatter(
                    x=[-Bh, -Bh, None, Bh, Bh, None, -Bh, Bh],
                    y=[0, H(0)/np.sqrt(2), None, 0, H(0)/np.sqrt(2), None, H(0)/np.sqrt(2), H(0)/np.sqrt(2)],
                    mode='lines',
                    line=dict(
                        color='gray',
                        dash='dash',
                    ),
                )
            ],
            layout=go.Layout(
                title='Gaussian pulse (spectrum)',
                xaxis=dict(
                    title='f',
                    range=[-2.0, 2.0],
                ),
                yaxis=dict(
                    title='H(f)',
                    range=[-0.1*H(0), 1.1*H(0)],
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'width': '50%', 'height': '400', 'display': 'inline-block'},
        id=uid('frequency-response-figure'),
    )
    return [figure_impulse_response, figure_frequency_response]
