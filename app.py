#!/usr/bin/env python3

import argparse

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.transform import radon, rescale, rotate

import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Parse input argument
ap = argparse.ArgumentParser();
ap.add_argument("-i", "--input", required=True)
args = vars(ap.parse_args());

# Read image as grayscale
image = cv2.imread(args["input"], 0);
image = rescale(image, scale=0.3, mode='reflect', multichannel=False);

# Pad image to square
image_width, image_height = image.shape;
image_shape_dif = abs(image_width-image_height);
image_shape_dif_first_half = int(image_shape_dif/2);
image_shape_dif_second_half = image_shape_dif-image_shape_dif_first_half;

# Padding on the (top, bottom) if image wdith is greater than height
# or (left, right) if image height is greater than width.
if image_width < image_height:
    padded_image = np.pad(image,
                        ((image_shape_dif_first_half,image_shape_dif_second_half),(0, 0)),
                        'constant',
                        constant_values=0);
else:
    padded_image = np.pad(image,
                        ((0,0),(image_shape_dif_first_half,image_shape_dif_second_half)),
                        'constant',
                        constant_values=0);

padded_image_file_name = './assets/padded-image.png';
plt.imsave(padded_image_file_name, padded_image, cmap=plt.cm.Greys_r);

padded_image_width, padded_image_height = padded_image.shape;

# Create radon transform
theta = np.linspace(0., 180., 180, endpoint=False);
sinogram = radon(image, theta=theta, circle=False);
sinogram = np.array(sinogram.T);
sinogram_width, sinogram_height = sinogram.shape;

# Save radon transform
sinogram_file_name = './assets/radon-transform.png';
plt.imsave(sinogram_file_name, sinogram, cmap=plt.cm.Greys_r);

# Extract data for plotting
x_data = [];
y_data = [];
for i in range(len(theta)):

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
    html.Hr(),

    html.Div(
        children='Use the slider to change the view of radon transform at different angle.',
        style={
            'textAlign': 'left'}
    ),
    html.Hr(),

    dcc.Slider(
        id='radon-slider',
        min=0,
        max=179,
        value=2,
        step=1
    ),
    html.Div(id='slider-output-container'),

    dcc.Graph(id='radon-transform'),

    # html.Div(id='rotated-image'),

    dcc.Graph(id='radon-transform-angle-view')

])

# Display rotated image with slider control
# @app.callback(
#     Output('rotated-image','children'),
#     [Input('radon-slider', 'value')]
# )
# def display_rotated_image(value):
#
#     rotated_image = rotate(padded_image, value);
#     rotated_image_file_name = "./assets/rotated_image_{}.png".format(value);
#
#     plt.imsave(rotated_image_file_name, rotated_image, cmap=plt.cm.Greys_r);
#
#     return html.Img(
#         src=rotated_image_file_name,
#         style={
#                     'height' : '30%',
#                     'width' : '30%',
#                     'marginLeft': 400
#                 })

# Add new trace line
@app.callback(
    Output('radon-transform', 'figure'),
    [Input('radon-slider', 'value')],
)
def update_trace_radon_transform(value):

    # Plot radon transform with annnotated line
    return {
        'data': [
            go.Scatter(
                x=(0, sinogram_height),
                y=(0, 179),
                mode="markers",
                showlegend=False
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
                source=sinogram_file_name,
                xref= "x",
                yref= "y",
                x= 0,
                y= 179,
                sizex= sinogram_height,
                sizey= 179,
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
                x1=sinogram_height,
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
    [Input('radon-slider', 'value')],
)
def display_value(value):
    return 'Angle: {}'.format(value)

# Display figure at different angle
@app.callback(
    Output('radon-transform-angle-view', 'figure'),
    [Input('radon-slider', 'value')],
)

# Update plots for sliders
def display_image_and_update_graph(value):

    rotated_image = rotate(padded_image, value);
    rotated_image_file_name = "./assets/rotated_image_{}.png".format(value);

    plt.imsave(rotated_image_file_name, rotated_image, cmap=plt.cm.Greys_r);

    yd = y_data[value];
    max_yd = np.amax(yd);

    x_min = int(sinogram_height/2-padded_image_width/2);
    x_max = padded_image_width;

    return {
        'data': [
            go.Scatter(
                y=yd

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
            images=[dict(
                source=rotated_image_file_name,
                xref= "x",
                yref= "y",
                x= x_min,
                y= max_yd,
                sizex= x_max,
                sizey= max_yd,
                sizing= "stretch",
                opacity= 1.0,
                visible = True,
                layer= "below")],
            template="plotly_white"
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
