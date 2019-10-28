#!/usr/bin/env python3

import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import cv2
from skimage.transform import radon

import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Parse input argument
ap = argparse.ArgumentParser();
ap.add_argument("-i", "--input", required=True)
args = vars(ap.parse_args());

# Create radon transform
image = cv2.imread(args["input"], 0);
theta = np.linspace(0., 180., 180, endpoint=False);
sinogram = radon(image, theta=theta, circle=False);
sinogram = np.array(sinogram.T)

# Create inputs
x_data = [];
y_data = [];
for i in range(len(theta)-1):

    yd = sinogram[i, :];
    x_data.append(i);
    y_data.append(yd);

# Create app layout
app.layout = html.Div([
    dcc.Graph(id='radon-transform'),

    dcc.Slider(
        id='angle--slider',
        min=0,
        max=179,
        value=0,
        step=1
    ),
    html.Div(id='slider-output-container')
])

# Display angle values
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('angle--slider', 'value')]
)
def display_value(value):
    return 'Angle: {}'.format(value)

# Display figure at different angle
@app.callback(
    Output('radon-transform', 'figure'),
    [Input('angle--slider', 'value')]
)

# Update plots for sliders
def update_graph(value):

    return {
        'data': [
            go.Scatter(
                y=y_data[value]

            )
        ],
        'layout': go.Layout(
            xaxis={
                'title': 'Position(pixel)'
            },
            yaxis={
                'title': 'Pixel'
            }
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
