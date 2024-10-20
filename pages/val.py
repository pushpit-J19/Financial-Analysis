import dash
import dash_core_components as dcc
from dash import callback
import dash_html_components as html
from dash import dash_table as dt
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from functions.dcf_calculator import calculate_intrinsic_pe, calculate_degree_of_overvaluation
from functions.scrape import scrape_screener_info, check_consolidated_available, get_top_ratios, get_range_tables, get_pnl_table, get_ratios

dash.register_page(__name__, path='/val', name = "DCF Valuation")

# layout = html.Div([
#     html.H1('This is our Archive page'),
#     html.Div('This is our Archive page content.')
# ])

# app.layout = [html.Div(children='Hello World')]

layout = html.Div(id="body", className = "px-5 py-3", children =[
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

    # Div of sliders
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


    # Div of Data points
    html.Br(),
    html.Div(children = [
        html.P(style={"line-height": "1.6"}, children = [
            html.Span("Stock Symbol: "), html.Span(id="stock_symbol_span"), html.Br(),
            html.Span("Current PE: "), html.Span(id="current_pe_span"), html.Br(),
            html.Span("FY23 PE (based on FY23 PAT as per mail): "), html.Span(id="fy23_pe_span"), html.Br(),
            html.Span("FY23 PE (based on reference web app to be replicated): "), html.Span(id="fy23_pe_span_2"), html.Br(),   # additional
            html.Span("5-yr median pre-tax RoCE: "), html.Span(id="median_roce_span"), html.Br(),
        ])
    ]),



    # DATA TABLES
    html.Br(),
    dt.DataTable(
        data = [{'': 'Sales Growth', '10 YRS': '0%', '5 YRS': '0%', '3 YRS': '0%', 'TTM': '0%'}, {'Particular': 'Profit Growth', '10 YRS': '0%', '5 YRS': '0%', '3 YRS': '0%', 'TTM': '0%'}],
        columns = [{"name": i, "id": i} for i in  ["", "10 YRS", "5 YRS", "3 YRS", "TTM"]],
        id = "year_data_table"
    ),



    # Graphs
    html.Br(),
    html.Div(
        id = "graph-holder",
        style = {"display": "flex"},
        children = [
            dcc.Graph( id="sales-graph", style={'display': 'inline-block'}, figure={}),
            dcc.Graph( id="profit-graph", style={'display': 'inline-block'}, figure={}),
        ]
    ),
    

    # Valuation Data points
    html.Br(),
    html.Div(children = [
        html.P(style={"line-height": "1.6"}, children = [
            html.Span("Play with inputs to see changes in intrinsic PE and overvaluation: "), html.Br(),
            html.Span("The calculated intrinsic PE is: "), html.Span(id="calc_pe_span"), html.Br(),
            html.Span("Degree of overvaluation (based on FY23 PAT as per mail): "), html.Span(id="overvaluation_span"), html.Span("%"), html.Br(),
            html.Span("Degree of overvaluation (based on reference web app to be replicated): "), html.Span(id="overvaluation_span_2"), html.Span("%"), html.Br(),     # additional
        ])
    ])

])

####################################################################################################################################################################################
# CALLBACK FUNCTIONS
####################################################################################################################################################################################

@callback(
    Output(component_id ='stock_symbol_span', component_property ='children'),
    Output(component_id ='current_pe_span', component_property ='children'),
    Output(component_id ='fy23_pe_span', component_property ='children'),
    Output(component_id ='fy23_pe_span_2', component_property ='children'),    # additional
    Output(component_id ='median_roce_span', component_property ='children'),

    Output(component_id ='year_data_table', component_property ='data'),
    # Output(component_id ='profit-graph', component_property ='figure'),
    
    Output(component_id ='calc_pe_span', component_property ='children'),
    Output(component_id ='overvaluation_span', component_property ='children'),
    Output(component_id ='overvaluation_span_2', component_property ='children'),     # additional
    # Output(component_id ='sales-graph', component_property ='figure'),
    # Output(component_id ='sales-graph', component_property ='figure'),
    Output(component_id ='graph-holder', component_property ='children'),

    Input(component_id ='symbol', component_property ='value'),
    Input(component_id ='coc-slider', component_property ='value'),
    Input(component_id ='roce-slider', component_property ='value'),
    Input(component_id ='growth-rate-slider', component_property ='value'),
    Input(component_id ='growth-years-slider', component_property ='value'),
    Input(component_id ='fade-years-slider', component_property ='value'),
    Input(component_id ='terminal-rate-slider', component_property ='value'),
)

def dcf_callback_function(symbol, coc, roce, g, g_period, fade_period, gt):
  
  status, soup = scrape_screener_info(symbol)
  
  
  if status == -1:
    return "Error: "+str(soup), 0, 0, 0, {}, 0, 0
  
  elif status == 200:

    pnl_section = soup.find("section", id="profit-loss")

    # TOP RATIOS
    try:
      top_ratios_data = get_top_ratios(soup)
      current_pe = round(float(top_ratios_data['Stock P/E']),2)
    except:
      current_pe = "NA"
    
    # 3, 5, 10 YEAR DATA
    try:
      year_data_tables_data = get_range_tables(pnl_section)
      years_data_df = pd.DataFrame(year_data_tables_data)[0:2]
      passed_year_data = years_data_df[["", "10 YRS", "5 YRS", "3 YRS", "TTM"]].to_dict('records')
    except:
      passed_year_data = [{'': 'Sales Growth', '10 YRS': '0%', '5 YRS': '0%', '3 YRS': '0%', 'TTM': '0%'}, {'Particular': 'Profit Growth', '10 YRS': '0%', '5 YRS': '0%', '3 YRS': '0%', 'TTM': '0%'}]


    # GRAPH
    try:
      tmp_df = years_data_df[["", "10 YRS", "5 YRS", "3 YRS", "TTM"]]
      tmp_df.set_index(tmp_df.columns[0], inplace = True)
      l = [col for col in tmp_df.columns.to_list()][:]
      print(l)
      print(tmp_df.loc["Sales Growth", :].to_list())
      fig1 = dcc.Graph(
                id="sales-graph",
                style={'display': 'inline-block'},
                figure={
                    "data": [
                        {
                            "x": tmp_df.loc["Sales Growth", :].to_list(),
                            "y": l,
                            "type": "bar",
                            "marker": {
                                "color": "#636efa",
                                },
                            "orientation": "h"
                        }
                    ],
                    
                    "layout": {
                        'title': '',
                        "xaxis": {"title": "Sales Growth %"},
                        "yaxis": {"title": "Time Period"},
                        'plot_bgcolor': "#e5ecf6",
                    },
                },
              )
      fig2 = dcc.Graph(
                id="profit-graph",
                style={'display': 'inline-block'},
                figure={
                    "data": [
                        {
                            "x": tmp_df.loc["Profit Growth", :].to_list(),
                            "y": l,
                            "type": "bar",
                            "marker": {
                                "color": "#636efa",
                                },
                            "orientation": "h"
                        }
                    ],
                    "layout": {
                        'title': '',
                        "xaxis": {"title": "Profit Growth %"},
                        "yaxis": {"title": "Time Period"},
                        'plot_bgcolor': "#e5ecf6",
                    },
                },
              )
    except:
      fig1 = dcc.Graph( id="sales-graph", style={'display': 'inline-block'}, figure={})
      fig2 = dcc.Graph( id="profit-graph", style={'display': 'inline-block'}, figure={})

    # PNL
    pnl_df = get_pnl_table(pnl_section)

    # fy23_pe
    try:
      if "Mar 2023" in pnl_df.columns.to_list():
        fy23PAT = pnl_df.loc["Net Profit", "Mar 2023"]
      elif "Dec 2023" in pnl_df.columns.to_list():
        fy23PAT = pnl_df.loc["Net Profit", "Dec 2023"]
      else:
        fy23PAT = pnl_df.loc["Net Profit", :].iloc[-3]  # -1 is TTM, -2 is current year, -3 is fy23
      fy23_pe = round(float(top_ratios_data["Market Cap"]) / fy23PAT, 2)
      fy23_pe_2 = round(float(top_ratios_data["Market Cap"]) / pnl_df.loc["Net Profit", :].iloc[-2], 2)       # additional
    except:
      fy23_pe = "NA"
      fy23_pe_2 = "NA"        # additional
    
    # RATIOS for ROCE
    try:
      ratio_df = get_ratios(soup)
      # print("here, ", "ROCE %" in ratio_df.index.to_list(), "ROE %" in ratio_df.index.to_list())
      if "ROCE %" in ratio_df.index.to_list():
        median_5yr_roce = round(float(ratio_df.loc["ROCE %", :].iloc[-7:-2].median()),2)
      elif "ROE %" in ratio_df.index.to_list():
        median_5yr_roce = round(float(ratio_df.loc["ROE %", :].iloc[-7:-2].median()),2)
      else:
        median_5yr_roce = "NA"
    except:
      median_5yr_roce = "NA"

    # DCF Calculations
    try:
      dcf_calc_df, dcf_metrics_dict = calculate_intrinsic_pe(coc/100, roce/100, g/100, g_period, fade_period, gt/100)
      intrinsic_pe = round(float(dcf_metrics_dict["TTM PE"]),2)

      # # Degree of overvaluation
      overvaluation = round(float(calculate_degree_of_overvaluation(current_pe, fy23_pe, intrinsic_pe) * 100),0)
      overvaluation_2 = round(float(calculate_degree_of_overvaluation(current_pe, fy23_pe_2, intrinsic_pe) * 100),0)  # additional
    except:
      intrinsic_pe = "NA"
      overvaluation = "NA"
      overvaluation_2 = "NA"  # additional


    # return symbol, current_pe, fy23_pe, str(median_5yr_roce) + "%", passed_year_data, round(intrinsic_pe, 2), overvaluation, [fig1,fig2]
    return symbol, current_pe, fy23_pe, fy23_pe_2, str(median_5yr_roce) + "%", passed_year_data, round(intrinsic_pe, 2), overvaluation, overvaluation_2, [fig1,fig2]


###################################################################################################
