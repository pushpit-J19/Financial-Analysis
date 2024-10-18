import dash
from dash import html

dash.register_page(__name__, path=['/', '/home'], name = "Home")

layout = html.Div([
    html.Div('This site provides interactive tools to valuate and analyze stocks through Reverse DCF model. Check the navigation bar for more.'),
])
