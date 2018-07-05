import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import komm
import numpy as np

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div(
        id=uid('graphs'),
        style={'width': '80%'},
    ),

    html.Div([
        html.Div([
            html.P(
                style={'margin-top': '32px'},
                id=uid('order-label'),
            ),
            dcc.Slider(
                id=uid('order-slider'),
                min=1,
                max=4,
                value=1,
                marks={i: str(2**i) for i in range(1, 5)},
                step=None,
                updatemode='drag',
            ),
            html.P(
                style={'margin-top': '32px'},
                id=uid('amplitude-label'),
            ),
            dcc.Slider(
                id=uid('amplitude-slider'),
                min=0.1,
                max=2.0,
                value=1.0,
                marks={0.1: '0.1', 1: '1.0', 2: '2.0'},
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
                value=0.0,
                step=np.pi/16,
            ),
            html.P(
                style={'margin-top': '32px'},
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

], style={'width': '100%', 'display': 'flex'})

@app.callback(
    dash.dependencies.Output(component_id=uid('order-label'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('order-slider'), component_property='value')]
)
def _(log_order):
    return 'Order: {}'.format(2**log_order)

@app.callback(
    dash.dependencies.Output(component_id=uid('phase-offset-slider'), component_property='marks'),
    [dash.dependencies.Input(component_id=uid('order-slider'), component_property='value')]
)
def _(log_order):
    marks = {-np.pi: '-π', 0: '0', np.pi: 'π'}
    M = 2**log_order
    if M <= 8:
        marks[np.pi/M] = 'π/{}'.format(M)
    return marks

@app.callback(
    dash.dependencies.Output(component_id=uid('amplitude-label'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('amplitude-slider'), component_property='value')]
)
def _(amplitude):
    return 'Amplitude: {:.2f}'.format(amplitude)

@app.callback(
    dash.dependencies.Output(component_id=uid('phase-offset-label'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('phase-offset-slider'), component_property='value')]
)
def _(phase_offset):
    return 'Phase offset: {:.2f}'.format(phase_offset)

@app.callback(
    dash.dependencies.Output(component_id=uid('noise-power-db-label'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('noise-power-db-slider'), component_property='value')]
)
def _(noise_power_db):
    return 'Noise power: {:.2f} dB'.format(noise_power_db)

@app.callback(
    dash.dependencies.Output(component_id=uid('graphs'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('order-slider'), component_property='value'),
     dash.dependencies.Input(component_id=uid('amplitude-slider'), component_property='value'),
     dash.dependencies.Input(component_id=uid('phase-offset-slider'), component_property='value'),
     dash.dependencies.Input(component_id=uid('noise-power-db-slider'), component_property='value')]
)
def psk_modulation_update(log_order, amplitude, phase_offset, noise_power_db):
    order = 2**log_order
    labeling = 'natural'
    modulation = komm.PSKModulation(order, amplitude, phase_offset, labeling)
    awgn = komm.AWGNChannel()

    num_symbols = 200*order
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
                    marker=dict(
                        size=2,
                        color='rgba(0, 0, 255, 0.5)',
                    ),
                ),
                go.Scatter(
                    name='Constellation',
                    x=np.real(modulation.constellation),
                    y=np.imag(modulation.constellation),
                    mode='markers',
                    marker=dict(
                        color='red',
                    ),
                ),
            ],
            layout=go.Layout(
                title=str(modulation),
                xaxis=dict(
                    title='Re',
                    range=[-2.1, 2.1],
                ),
                yaxis=dict(
                    title='Im',
                    range=[-2.1, 2.1],
                    scaleanchor = 'x',
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),

        id=uid('constellation-figure'),
    )

    return [constellation_figure]
