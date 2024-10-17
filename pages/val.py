import dash
import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table as dt
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path='/val', name = "DCF Valuation")

# layout = html.Div([
#     html.H1('This is our Archive page'),
#     html.Div('This is our Archive page content.')
# ])

# app.layout = [html.Div(children='Hello World')]

layout = html.Div(id="body", children =[
    html.Div(children = [
      html.H1("Valuing Consistent Compounders"),
      html.P("Hi there!"),
      html.P("This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model."),
      html.P("We then compare this with current PE of the stock to calculate degree of overvaluation."),
    ]),

    html.Div(children = [
        html.Label("NSE/BSE Symbol"),
        html.Br(),
        dcc.Input(value = "NESTLEIND", type="text", id="symbol"),
    ]),

    html.Br(),

    html.Div(children=[
        html.Label("Cost of Capital (CoC): % ", htmlFor = "coc-slider"),
        dcc.Slider(
            id = "coc-slider",
            min = 8,
            max = 16,
            value = 12,
            marks = {i:i for i in range (8,17)},
            step = 0.5
        ),

        html.Label("Return on Capital Employed (RoCE): % ", htmlFor = "roce-slider"),
        dcc.Slider(
            id = "roce-slider",
            min = 10,
            max = 100,
            value = 20,
            marks = {i:i for i in range (10,101,10)},
            step = 5
        ),

        html.Label("Growth during high growth period: $ ", htmlFor = "growth-rate-slider"),
        dcc.Slider(
            id = "growth-rate-slider",
            min = 8,
            max = 20,
            value = 12,
            marks = {i:i for i in range (8,21,2)},
            step = 1
        ),

        html.Label("High growth period(years) ", htmlFor = "growth-years-slider"),
        dcc.Slider(
            id = "growth-years-slider",
            min = 10,
            max = 25,
            value = 15,
            step = 1,
            marks = {i:i for i in range (10,26,2)} | {25: 25},
        ),

        html.Label("Fade period(years): ", htmlFor = "fade-years-slider"),
        dcc.Slider(
            id = "fade-years-slider",
            min = 5,
            max = 20,
            value = 15,
            step = 5,
            marks = {i:i for i in range (5,21,5)},
        ),

        html.Label("Terminal growth rate: % ", htmlFor = "terminal-rate-slider"),
        dcc.Slider(
            id = "terminal-rate-slider",
            min = 0,
            max = 7.5,
            value = 5,
            step = 0.5,
            marks = {i:i for i in range (0, 8)} | {7.5:7.5},
        ),
    ]),


    # DATA TABLES
    dt.DataTable(
        [{'Particular': 'Compounded Sales Growth', '10 Years': '10%', '5 Years': '17%', '3 Years': '22%', 'TTM': '5%'}, {'Particular': 'Compounded Profit Growth', '10 Years': '13%', '5 Years': '20%', '3 Years': '24%', 'TTM': '10%'}, {'Particular': 'Stock Price CAGR', '10 Years': '15%', '5 Years': '10%', '3 Years': '7%', '1 Year': '2%'}, {'Particular': 'Return on Equity', '10 Years': '68%', '5 Years': '107%', '3 Years': '121%', 'Last Year': '135%'}],
        [{"name": i, "id": i} for i in  ["Particular", "10 Years", "5 Years", "3 Years", "TTM", "1 Year", "Last Year"]],
        id = "year_data_table"
    )


])

