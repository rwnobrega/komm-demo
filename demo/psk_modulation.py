import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import komm
import numpy as np

class PSKDemo:
    def __init__(self, **kwargs):
        self._parameters = kwargs
        self._simulate()

    def update_parameters(self, **kwargs):
        if kwargs != self._parameters:
            self._parameters = kwargs
            self._simulate()

    def __getitem__(self, key):
        return self._parameters.get(key, None)

    def _simulate(self):
        order = 2**self._parameters['log_order']
        amplitude = self._parameters['amplitude']
        phase_offset = self._parameters['phase_offset']
        labeling = self._parameters['labeling']
        noise_power_db = self._parameters['noise_power_db']

        modulation = komm.PSKModulation(order, amplitude, phase_offset, labeling)
        modulation._constellation = np.round(modulation._constellation, 12)  # Only for pedagogical reasons
        awgn = komm.AWGNChannel()
        num_symbols = 200*order
        noise_power = 10**(noise_power_db / 10)
        awgn.signal_power = modulation.energy_per_symbol
        awgn.snr = awgn.signal_power / noise_power
        num_bits = modulation.bits_per_symbol * num_symbols
        bits = np.random.randint(2, size=num_bits)
        sentword = modulation.modulate(bits)
        recvword = awgn(sentword)

        self.output = {
            'title': str(modulation),
            'constellation': modulation.constellation,
            'labels': [''.join(str(b) for b in komm.util.int2binlist(modulation.labeling[i], width=modulation.bits_per_symbol)) for i in range(order)],
            'gaussian_clouds': recvword,
        }

demo = PSKDemo(
    log_order=1,
    amplitude=1.0,
    phase_offset=0.0,
    labeling='reflected',
    noise_power_db=-20.0
)


from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div(
        dcc.Graph(
            id=uid('constellation-graph'),
        ),
        style={'width': '78%'},
    ),

    html.Div([
        html.P(
            style={'margin-top': '32px'},
            id=uid('order-label'),
        ),
        dcc.Slider(
            id=uid('log-order-slider'),
            min=1,
            max=4,
            value=demo['log_order'],
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
            value=demo['amplitude'],
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
            value=demo['phase_offset'],
            step=np.pi/16,
        ),
        html.P(
            'Labeling:',
            style={'margin-top': '32px'},
        ),
        dcc.Dropdown(
            id=uid('labeling-dropdown'),
            options=[
                {'label': 'Reflected (Gray)', 'value': 'reflected'},
                {'label': 'Natural', 'value': 'natural'},
            ],
            value=demo['labeling'],
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
            value=demo['noise_power_db'],
            marks={-40: '-40', 10: '10'},
            step=0.01,
        )],

        style={'width': '20%', 'flex-grow:': '1'},
    ),

], style={'display': 'flex'})

@app.callback(
    Output(component_id=uid('order-label'), component_property='children'),
    [Input(component_id=uid('log-order-slider'), component_property='value')]
)
def _(log_order):
    return 'Order: {}'.format(2**log_order)

@app.callback(
    Output(component_id=uid('phase-offset-slider'), component_property='marks'),
    [Input(component_id=uid('log-order-slider'), component_property='value')]
)
def _(log_order):
    marks = {-np.pi: '-π', 0: '0', np.pi: 'π'}
    order = 2**log_order
    if order <= 8:
        marks[np.pi/order] = 'π/{}'.format(order)
    return marks

@app.callback(
    Output(component_id=uid('amplitude-label'), component_property='children'),
    [Input(component_id=uid('amplitude-slider'), component_property='value')]
)
def _(amplitude):
    return 'Amplitude: {:.2f}'.format(amplitude)

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
    Output(component_id=uid('constellation-graph'), component_property='figure'),
    [Input(component_id=uid('log-order-slider'), component_property='value'),
     Input(component_id=uid('amplitude-slider'), component_property='value'),
     Input(component_id=uid('phase-offset-slider'), component_property='value'),
     Input(component_id=uid('labeling-dropdown'), component_property='value'),
     Input(component_id=uid('noise-power-db-slider'), component_property='value'),
     Input(component_id=uid('constellation-graph'), component_property='relayoutData')],
    [State(component_id=uid('constellation-graph'), component_property='figure')]
)
def psk_modulation_update(log_order, amplitude, phase_offset, labeling, noise_power_db, relayoutData, figure):
    demo.update_parameters(
        log_order=log_order,
        amplitude=amplitude,
        phase_offset=phase_offset,
        labeling=labeling,
        noise_power_db=noise_power_db
    )

    old_layout = figure['layout'] if figure else None
    old_data = figure['data'] if figure else None

    figure = go.Figure(
        data=[
            go.Scatter(
                name='Constellation',
                x=np.real(demo.output['constellation']),
                y=np.imag(demo.output['constellation']),
                mode='markers+text',
                text=demo.output['labels'],
                textposition='top center',
                marker={'color': 'red'},
                textfont = {'size': 10},
                visible=True,
            ),
            go.Scatter(
                name='Gaussian clouds',
                x=np.real(demo.output['gaussian_clouds']),
                y=np.imag(demo.output['gaussian_clouds']),
                mode='markers',
                marker={'size': 2, 'color': 'rgba(0, 0, 255, 0.2)'},
                visible='legendonly',
            ),
        ],

        layout=go.Layout(
            xaxis=dict(
                title='Re',
                range=(-2.1, 2.1),
            ),
            yaxis=dict(
                title='Im',
                range=(-2.1, 2.1),
                scaleanchor = 'x',
            ),
            hovermode='closest',
        ),
    )

    if old_layout:
        figure['layout'] = old_layout

    figure['layout']['title'] = demo.output['title']

    for axis in ['xaxis', 'yaxis']:
        if figure['layout'][axis]['autorange']:
            figure['layout'][axis]['autorange'] = False
            figure['layout'][axis]['range'] = (-2.1, 2.1)

    if old_data:
        for i, trace in enumerate(old_data):
            figure['data'][i]['visible'] = trace['visible']

    return figure
