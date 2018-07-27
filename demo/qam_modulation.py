import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import komm
import numpy as np

class QAMDemo:
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
        phase_offset = self._parameters['phase_offset']
        labeling = self._parameters['labeling']
        noise_power_db = self._parameters['noise_power_db']

        if self._parameters['square']:
            orders = 4**self._parameters['log_order_0']
            base_amplitudes = self._parameters['base_amplitude_0']
        else:
            orders = ( 2**self._parameters['log_order_0'],  2**self._parameters['log_order_1'])
            base_amplitudes = (self._parameters['base_amplitude_0'], self._parameters['base_amplitude_1'])

        modulation = komm.QAModulation(orders, base_amplitudes, phase_offset, labeling)
        modulation._constellation = np.round(modulation._constellation, 12)  # Only for pedagogical reasons
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

        self.output = {
            'title': str(modulation),
            'constellation': modulation.constellation,
            'labels': [''.join(str(b) for b in komm.int2binlist(modulation.labeling[i], width=modulation.bits_per_symbol)) for i in range(order)],
            'gaussian_clouds': recvword,
        }

demo = QAMDemo(
    square=True,
    log_order_0=1,
    log_order_1=1,
    base_amplitude_0=1.0,
    base_amplitude_1=1.0,
    phase_offset=0.0,
    labeling='reflected_2d',
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
        dcc.Checklist(
            options=[
                {'label': 'Square', 'value': 'Square'},
            ],
            values=['Square'],
            id=uid('square-checklist'),
        ),
        html.P(
            style={'margin-top': '32px'},
            id=uid('order-label'),
        ),
        dcc.Slider(
            id=uid('log-order-0-slider'),
            min=1,
            max=3,
            value=demo['log_order_0'],
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
            value=demo['log_order_1'],
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
            value=demo['base_amplitude_0'],
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
            value=demo['base_amplitude_1'],
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
                {'label': 'Reflected 2D (Gray)', 'value': 'reflected_2d'},
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
    Output(component_id=uid('base-amplitude-1-slider'), component_property='style'),
    [Input(component_id=uid('square-checklist'), component_property='values')]
)
def _(square_checklist):
    if square_checklist == ['Square']:
        return {'display': 'none'}
    else:
        return {}

@app.callback(
    Output(component_id=uid('log-order-1-slider'), component_property='style'),
    [Input(component_id=uid('square-checklist'), component_property='values')]
)
def _(square_checklist):
    if square_checklist == ['Square']:
        return {'display': 'none'}
    else:
        return {}

@app.callback(
    Output(component_id=uid('log-order-0-slider'), component_property='marks'),
    [Input(component_id=uid('square-checklist'), component_property='values')]
)
def _(square_checklist):
    if square_checklist == ['Square']:
        return {i: str(4**i) for i in range(1, 4)}
    else:
        return {i: str(2**i) for i in range(1, 4)}


@app.callback(
    Output(component_id=uid('order-label'), component_property='children'),
    [Input(component_id=uid('log-order-0-slider'), component_property='value'),
     Input(component_id=uid('log-order-1-slider'), component_property='value'),
     Input(component_id=uid('square-checklist'), component_property='values')]
)
def _(log_order_0, log_order_1, square_checklist):
    if square_checklist == ['Square']:
        return 'Order: {}'.format(4**log_order_0)
    else:
        return 'Orders: ({}, {})'.format(2**log_order_0, 2**log_order_1)

@app.callback(
    Output(component_id=uid('base-amplitudes-label'), component_property='children'),
    [Input(component_id=uid('base-amplitude-0-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-1-slider'), component_property='value'),
     Input(component_id=uid('square-checklist'), component_property='values')]
)
def _(base_amplitude_0, base_amplitude_1, square_checklist):
    if square_checklist == ['Square']:
        return 'Base amplitude: {:.2f}'.format(base_amplitude_0)
    else:
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
    Output(component_id=uid('constellation-graph'), component_property='figure'),
    [Input(component_id=uid('square-checklist'), component_property='values'),
     Input(component_id=uid('log-order-0-slider'), component_property='value'),
     Input(component_id=uid('log-order-1-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-0-slider'), component_property='value'),
     Input(component_id=uid('base-amplitude-1-slider'), component_property='value'),
     Input(component_id=uid('phase-offset-slider'), component_property='value'),
     Input(component_id=uid('labeling-dropdown'), component_property='value'),
     Input(component_id=uid('noise-power-db-slider'), component_property='value')],
    [State(component_id=uid('constellation-graph'), component_property='figure')]
)
def qam_modulation_update(square_checklist, log_order_0, log_order_1, base_amplitude_0, base_amplitude_1, phase_offset, labeling, noise_power_db, figure):
    demo.update_parameters(
        square=square_checklist == ['Square'],
        log_order_0=log_order_0,
        log_order_1=log_order_1,
        base_amplitude_0=base_amplitude_0,
        base_amplitude_1=base_amplitude_1,
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
            ),
            yaxis=dict(
                title='Im',
                scaleanchor = 'x',
            ),
            hovermode='closest',
        ),
    )

    if old_layout:
        figure['layout'] = old_layout

    figure['layout']['title'] = demo.output['title']

    if old_data:
        for i, trace in enumerate(old_data):
            figure['data'][i]['visible'] = trace['visible']

    return figure
