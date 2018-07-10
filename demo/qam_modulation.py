import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

import komm
import numpy as np

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div(
        id=uid('graphs'),
        style={'width': '78%'},
    ),

    html.Div([
        html.Div([
            html.P(
                style={'margin-top': '32px'},
                id=uid('order-label'),
            ),
            dcc.Slider(
                id=uid('log-order-0-slider'),
                min=1,
                max=3,
                value=1,
                marks={i: str(2**i) for i in range(1, 4)},
                step=None,
                updatemode='drag',
            ),
            html.P(
                style={'margin-top': '24px'},
            ),
            dcc.Slider(
                id=uid('log-order-1-slider'),
                min=1,
                max=3,
                value=1,
                marks={i: str(2**i) for i in range(1, 4)},
                step=None,
                updatemode='drag',
            ),
            html.P(
                style={'margin-top': '32px'},
                id=uid('base-amplitudes-label'),
            ),
            dcc.Slider(
                id=uid('base-amplitude-0-slider'),
                min=0.5,
                max=1.5,
                value=1.0,
                marks={0.5: '0.5', 1: '1.0', 1.5: '1.5'},
                step=0.01,
            ),
            html.P(
                style={'margin-top': '24px'},
            ),
            dcc.Slider(
                id=uid('base-amplitude-1-slider'),
                min=0.5,
                max=1.5,
                value=1.0,
                marks={0.5: '0.5', 1: '1.0', 1.5: '1.5'},
                step=0.01,
            ),
            html.P(
                style={'margin-top': '32px'},
                id=uid('phase-offset-label'),
            ),
            dcc.Slider(
                id=uid('phase-offset-slider'),
                min=-np.pi,
                max=np.pi,
                marks = {-np.pi: '-π', -np.pi/2: '-π/2', -np.pi/4: '-π/4', 0: '0', np.pi/4: 'π/4', np.pi/2: 'π/2', np.pi: 'π'},
                value=0.0,
                step=np.pi/16,
            ),
            html.P(
                'Labeling:',
                style={'margin-top': '32px'},
            ),
            dcc.Dropdown(
                id=uid('labeling-dropdown'),
                options=[
                    {'label': 'Reflected 2D (Gray)', 'value': 'reflected_2d'},
                    {'label': 'Natural', 'value': 'natural'},
                ],
                value='reflected_2d',
                clearable=False,
            ),
            html.P(
                style={'margin-top': '16px'},
                id=uid('noise-power-db-label'),
            ),
            dcc.Slider(
                id=uid('noise-power-db-slider'),
                min=-40.0,
                max=10.0,
                value=-40.0,
                marks={-40: '-40', 10: '10'},
                step=0.01,
            )],
        )],

        style={'width': '20%', 'flex-grow:': '1'},
    ),

], style={'display': 'flex'})

@app.callback(
    Output(component_id=uid('order-label'), component_property='children'),
    [Input(component_id=uid('log-order-0-slider'), component_property='value'),
     Input(component_id=uid('log-order-1-slider'), component_property='value')]
)
def _(log_order_0, log_order_1):
    order_0 = 2**log_order_0
    order_1 = 2**log_order_1
    return 'Orders: ({}, {})'.format(order_0, order_1)

@app.callback(
    Output(component_id=uid('base-amplitudes-label'), component_property='children'),
    [Input(component_id=uid('base-amplitude-0-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-1-slider'), component_property='value')]
)
def _(base_amplitude_0, base_amplitude_1):
    return 'Base amplitudes: ({:.2f}, {:.2f})'.format(base_amplitude_0, base_amplitude_1)

@app.callback(
    Output(component_id=uid('phase-offset-label'), component_property='children'),
    [Input(component_id=uid('phase-offset-slider'), component_property='value')]
)
def _(phase_offset):
    return 'Phase offset: {:.2f}'.format(phase_offset)

@app.callback(
    Output(component_id=uid('noise-power-db-label'), component_property='children'),
    [Input(component_id=uid('noise-power-db-slider'), component_property='value')]
)
def _(noise_power_db):
    return 'Noise power: {:.2f} dB'.format(noise_power_db)

@app.callback(
    Output(component_id=uid('graphs'), component_property='children'),
    [Input(component_id=uid('log-order-0-slider'), component_property='value'),
     Input(component_id=uid('log-order-1-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-0-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-1-slider'), component_property='value'),
     Input(component_id=uid('phase-offset-slider'), component_property='value'),
     Input(component_id=uid('labeling-dropdown'), component_property='value'),
     Input(component_id=uid('noise-power-db-slider'), component_property='value')]
)
def qam_modulation_update(log_order_0, log_order_1, base_amplitude_0, base_amplitude_1, phase_offset, labeling, noise_power_db):
    order_0 = 2**log_order_0
    order_1 = 2**log_order_1
    modulation = komm.QAModulation((order_0, order_1), (base_amplitude_0, base_amplitude_1), phase_offset, labeling)
    awgn = komm.AWGNChannel()

    order = modulation.order
    num_symbols = 100*order
    noise_power = 10**(noise_power_db / 10)
    awgn.signal_power = modulation.energy_per_symbol
    awgn.snr = awgn.signal_power / noise_power
    num_bits = modulation.bits_per_symbol * num_symbols
    bits = np.random.randint(2, size=num_bits)
    sentword = modulation.modulate(bits)
    recvword = awgn(sentword)

    constellation_figure = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    name='Gaussian clouds',
                    x=np.real(recvword),
                    y=np.imag(recvword),
                    mode='markers',
                    marker={'size': 2, 'color': 'rgba(0, 0, 255, 0.33)'},
                ),
                go.Scatter(
                    name='Constellation',
                    x=np.real(modulation.constellation),
                    y=np.imag(modulation.constellation),
                    mode='markers',
                    marker={'color': 'red'},
                ),
                go.Scatter(
                    name='Labeling',
                    x=np.real(modulation.constellation),
                    y=np.imag(modulation.constellation) + 0.25,
                    mode='text',
                    text=[''.join(str(b) for b in komm.util.int2binlist(modulation.labeling[i], width=modulation.bits_per_symbol)) for i in range(order)],
                    textposition='top center',
                    textfont = {'size': 10},
                ),
            ],
            layout=go.Layout(
                title=str(modulation),
                xaxis=dict(
                    title='Re',
                    range=[-1.5*order_0 - 1, 1.5*order_0 + 1],
                    scaleanchor = 'y',
                ),
                yaxis=dict(
                    title='Im',
                    range=[-1.5*order_1 - 1, 1.5*order_1 + 1],
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),

        id=uid('constellation-figure'),
    )

    return [constellation_figure]
