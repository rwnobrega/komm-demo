import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from app import app, uid_gen

uid = uid_gen(__name__)

layout = html.Div([
    html.Label('Length:'),

    html.Div([
        dcc.Slider(
            id=uid('length-slider'),
            min=2,
            max=13,
            value=2,
            marks={length: str(length) for length in [2, 3, 4, 5, 7, 11, 13]},
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
    Output(component_id=uid('graphs'), component_property='children'),
    [Input(component_id=uid('length-slider'), component_property='value')]
)
def barker_sequence_update(length):
    barker = komm.BarkerSequence(length=length)
    shifts = np.arange(-length - 1, length + 2)

    figure_sequence = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=np.arange(length + 1),
                    y=np.pad(barker.polar_sequence, (0, 1), mode='edge'),
                    mode='lines',
                    line=dict(
                        shape='hv',
                    ),
                ),
            ],
            layout=go.Layout(
                title=str(barker),
                xaxis=dict(
                    title='n',
                    dtick=1.0,
                ),
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

    figure_autocorrelation = dcc.Graph(
        figure=go.Figure(
            data=[
                go.Scatter(
                    x=shifts,
                    y=barker.autocorrelation(shifts),
                    mode='lines',
                ),
            ],
            layout=go.Layout(
                title='Autocorrelation',
                xaxis=dict(
                    title='ℓ',
                ),
                yaxis=dict(
                    title='R[ℓ]',
                ),
                margin={'l': 60, 'b': 60, 't': 80, 'r': 60},
            ),
        ),
        style={'display': 'inline-block', 'width': '50%'},
        id=uid('autocorrelation-figure'),
    )

    return [figure_sequence, figure_autocorrelation]
