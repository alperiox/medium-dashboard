import dash
from dash import Dash, html, dcc

dash.register_page(__name__)

layout = html.Div([
    html.H1("Made in progress!", className='text-justify font-weight-light bg-primary text-white ')
])