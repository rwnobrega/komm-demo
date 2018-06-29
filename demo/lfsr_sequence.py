import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Label('Degree:'),

    html.Div([
        dcc.Slider(
            id=uid('degree-slider'),
            min=2,
            max=7,
            value=2,
            marks={length: str(length) for length in range(2, 8)},
            step=None,
            updatemode='drag',
        )
    ], style={'margin-bottom': '25px', 'align': 'center'}),

    html.Div(
        id=uid('graphs'),
    ),
])

# ---

import komm
import numpy as np


@app.callback(
    dash.dependencies.Output(component_id=uid('graphs'), component_property='children'),
    [dash.dependencies.Input(component_id=uid('degree-slider'), component_property='value')]
)
def lfsr_sequence_update(degree):
    lfsr = komm.LFSRSequence.maximum_length_sequence(degree=degree)
    length = lfsr.length
    shifts = np.arange(-2*length + 1, 2*length)

    figure_sequence = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=np.arange(length + 1),
                    y=np.pad(lfsr.polar_sequence, (0, 1), mode='edge'),
                    mode='lines',
                    line=dict(
                        shape='hv',
                    ),
                ),
            ],
            layout=go.Layout(
                title=str(lfsr),
                yaxis=dict(
                    title='a[n]',
                    dtick=1.0,
                ),
            margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'display': 'inline-block', 'width': '50%'},
        id=uid('sequence-figure'),
    )

    figure_cyclic_autocorrelation = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=shifts,
                    y=lfsr.cyclic_autocorrelation(shifts, normalized=True),
                    mode='lines',
                ),
            ],
            layout=go.Layout(
                title='Cyclic autocorrelation (normalized)',
                xaxis=dict(
                    title='ℓ',
                ),
                yaxis=dict(
                    title='R~[ℓ]',
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'display': 'inline-block', 'width': '50%'},
        id=uid('cyclic-autocorrelation-figure'),
    )

    return [figure_sequence, figure_cyclic_autocorrelation]
