#!/usr/bin/env python3

import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import cv2
import matplotlib.pyplot as plt
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
sinogram = np.array(sinogram.T);

# Save radon transform
file_name = './assets/radon-transform.png';
plt.imsave(file_name, sinogram, cmap=plt.cm.Greys_r);

# Extract data for plotting
x_data = [];
y_data = [];
for i in range(len(theta)-1):

    yd = sinogram[i, :];
    x_data.append(i);
    y_data.append(yd);

# Create app layout
app.layout = html.Div([
    html.H1(
        children='Radon Transform Visualisation',
        style={
            'textAlign': 'center'}
    ),

    html.Div(
        children='A web application for visualising radon transform.',
        style={
            'textAlign': 'center'}
    ),

    html.Img(
        src=args["input"],
        style={
                    'height' : '50%',
                    'width' : '50%',
                    'float' : 'top',
                    'position' : 'relative',
                    'padding-top' : 0,
                    'padding-right' : 0
                }),
    dcc.Slider(
        id='radon--slider',
        min=0,
        max=179,
        value=0,
        step=1
    ),
    dcc.Graph(id='radon-transform'),

    dcc.Graph(id='radon-transform-angle-view'),

    dcc.Slider(
        id='angle--slider',
        min=0,
        max=179,
        value=0,
        step=1
    ),
    html.Div(id='slider-output-container')
])

# Add new trace line
@app.callback(
    Output('radon-transform', 'figure'),
    [Input('radon--slider', 'value')],
)
def update_trace_radon_transform(value):

    return {
        'data': [
            go.Scatter(
                x=(0, 1447),
                y=(0, 179),
                mode="markers",
                showlegend=False,

            ),
            go.Scatter(
                x=[20],
                y=[179-value],
                name="Angle:{}".format(value),
                mode="text"
            )

        ],
        'layout': go.Layout(
            xaxis={
                'title': 'Pixel values',
                'showgrid': False,
                'zeroline': False
            },
            yaxis={
                'title': 'Angle',
                'showgrid': False,
                'zeroline': False
            },
            margin = dict(l=40, r=10, t=10, b=40),
            images=[dict(
                source=file_name,
                xref= "x",
                yref= "y",
                x= 0,
                y= 180,
                sizex= 1448,
                sizey= 180,
                sizing= "stretch",
                opacity= 1.0,
                visible = True,
                layer= "below")],
            template="plotly_white",
            shapes=[dict(
                type="line",
                xref="x",
                yref="y",
                x0=0,
                y0=179-value,
                x1=1447,
                y1=179-value,
                line=dict(
                    color="LightSeaGreen",
                    width=3,
                    )
            )]
        )
    }


# Display angle values
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('angle--slider', 'value')]
)
def display_value(value):
    return 'Angle: {}'.format(value)

# Display figure at different angle
@app.callback(
    Output('radon-transform-angle-view', 'figure'),
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
                'title': 'Position (pixel)'
            },
            yaxis={
                'title': 'Pixel values'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
