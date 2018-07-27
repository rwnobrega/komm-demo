import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

import komm
import numpy as np

class UniformQuantizationDemo:
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
        num_levels = self._parameters['num_levels']
        input_peak = self._parameters['input_peak']
        choice = self._parameters['choice']

        quantizer = komm.UniformQuantizer(num_levels, input_peak, choice)
        x = np.linspace(-2.0*input_peak, 2.0*input_peak, 1000)
        y = quantizer(x)

        self.output = {
            'title': str(quantizer),
            'input_signal': x,
            'output_signal': y,
        }

demo = UniformQuantizationDemo(
    num_levels=4,
    input_peak=1.0,
    choice='mid-riser',
)


from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Div(
        dcc.Graph(
            id=uid('quantizer-graph'),
        ),
        style={'width': '78%'},
    ),

    html.Div([
        html.P(
            style={'margin-top': '32px'},
            id=uid('num-levels-label'),
        ),
        dcc.Slider(
            id=uid('num-levels-slider'),
            min=2,
            max=32,
            value=demo['num_levels'],
            marks={2**i: str(2**i) for i in range(1, 6)},
            updatemode='drag',
        ),
        html.P(
            style={'margin-top': '32px'},
            id=uid('input-peak-label'),
        ),
        dcc.Slider(
            id=uid('input-peak-slider'),
            min=0.1,
            max=2.0,
            value=demo['input_peak'],
            marks={0.1: '0.1', 1: '1.0', 2: '2.0'},
            step=0.01,
            updatemode='drag',
        ),
        html.P(
            'Choice:',
            style={'margin-top': '32px'},
        ),
        dcc.Dropdown(
            id=uid('choice-dropdown'),
            options=[
                {'label': 'Unsigned', 'value': 'unsigned'},
                {'label': 'Signed (mid-riser)', 'value': 'mid-riser'},
                {'label': 'Signed (mid-tread)', 'value': 'mid-tread'},
            ],
            value=demo['choice'],
            clearable=False,
        )],

        style={'width': '20%', 'flex-grow:': '1'},
    ),

], style={'display': 'flex'})

@app.callback(
    Output(component_id=uid('num-levels-label'), component_property='children'),
    [Input(component_id=uid('num-levels-slider'), component_property='value')]
)
def _(num_levels):
    return 'Numer of levels: {}'.format(num_levels)

@app.callback(
    Output(component_id=uid('input-peak-label'), component_property='children'),
    [Input(component_id=uid('input-peak-slider'), component_property='value')]
)
def _(input_peak):
    return 'Input peak: {:.2f}'.format(input_peak)

@app.callback(
    Output(component_id=uid('quantizer-graph'), component_property='figure'),
    [Input(component_id=uid('num-levels-slider'), component_property='value'),
     Input(component_id=uid('input-peak-slider'), component_property='value'),
     Input(component_id=uid('choice-dropdown'), component_property='value'),
     Input(component_id=uid('quantizer-graph'), component_property='relayoutData')],
    [State(component_id=uid('quantizer-graph'), component_property='figure')]
)
def uniform_quantization_update(num_levels, input_peak, choice, relayoutData, figure):
    demo.update_parameters(
        num_levels=num_levels,
        input_peak=input_peak,
        choice=choice,
    )

    old_layout = figure['layout'] if figure else None
    old_data = figure['data'] if figure else None

    figure = go.Figure(
        data=[
            go.Scatter(
                name='Characteristic curve',
                x=demo.output['input_signal'],
                y=demo.output['output_signal'],
                textposition='top center',
                marker={'color': 'red'},
                textfont = {'size': 10},
                visible=True,
            ),
        ],

        layout=go.Layout(
            xaxis=dict(
                title='Input',
                range=(-2.1, 2.1),
            ),
            yaxis=dict(
                title='Output',
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
