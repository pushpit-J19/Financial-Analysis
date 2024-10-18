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
            html.Span("FY23 PE: "), html.Span(id="fy23_pe_span"), html.Br(),
            html.Span("5-yr median pre-tax RoCE: "), html.Span(id="median_roce_span"), html.Br(),
        ])
    ]),


    # DATA TABLES
    html.Br(),
    dt.DataTable(
        data = [{'': 'Sales Growth', '10 Years': '0%', '5 Years': '0%', '3 Years': '0%', 'TTM': '0%'}, {'Particular': 'Profit Growth', '10 Years': '0%', '5 Years': '0%', '3 Years': '0%', 'TTM': '0%'}],
        columns = [{"name": i, "id": i} for i in  ["", "10 Years", "5 Years", "3 Years", "TTM"]],
        id = "year_data_table"
    ),



    # Graphs
    html.Br(),

    html.Div(children = [
        dcc.Graph(
          figure={
              'data': [
                  {'x': [21,22,30,70], 'y': ["TTM", "3 yrs", "5 yrs", "10 yrs"], 'type': 'bar', 'name': 'SF', "orientation": "h"},
              ],
              "layout" : {
                'title' : 'Sales Growth %',
                'plot_bgcolor': "#eee",
                "paper_bgcolor" : "teal",
                'font' : {
                    'color': 'white'
                  }
              }
            }              
          )
        ]),
    

    # Valuation Data points
    html.Br(),
    html.Div(children = [
        html.P(style={"line-height": "1.6"}, children = [
            html.Span("Play with inputs to see changes in intrinsic PE and overvaluation: "), html.Br(),
            html.Span("The calculated intrinsic PE is: "), html.Span(id="calc_pe_span"), html.Br(),
            html.Span("Degree of overvaluation: "), html.Span(id="overvaluation_span"), html.Span("%"), html.Br(),
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
    Output(component_id ='median_roce_span', component_property ='children'),
    Output(component_id ='year_data_table', component_property ='data'),
    # Output(component_id ='graphs1', component_property ='children'),
    # Output(component_id ='graphs2', component_property ='children'),
    Output(component_id ='calc_pe_span', component_property ='children'),
    Output(component_id ='overvaluation_span', component_property ='children'),

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
    return "Error: "+str(e), 0, 0, 0, {}, 0, 0
  
  elif status == 200:

    pnl_section = soup.find("section", id="profit-loss")

    # TOP RATIOS
    top_ratios_data = get_top_ratios(soup)
    current_pe = round(float(top_ratios_data['Stock P/E']),2)
    
    # 3, 5, 10 YEAR DATA
    year_data_tables_data = get_range_tables(pnl_section)
    years_data_df = pd.DataFrame(year_data_tables_data)[0:2]

    # PNL
    pnl_df = get_pnl_table(pnl_section)

    # fy23_pe
    if "Mar 2023" in pnl_df.columns.to_list():
      fy23PAT = pnl_df.loc["Net Profit", "Mar 2023"]
    elif "Dec 2023" in pnl_df.columns.to_list():
      fy23PAT = pnl_df.loc["Net Profit", "Dec 2023"]
    else:
      fy23PAT = pnl_df.loc["Net Profit", :].iloc[-3]  # -1 is TTM, -2 is current year, -3 is fy23
    fy23_pe = round(float(top_ratios_data["Market Cap"]) / fy23PAT, 2)
    
    # RATIOS for ROCE
    ratio_df = get_ratios(soup)
    median_5yr_roce = round(float(ratio_df.loc["ROCE %", :].iloc[-7:-2].median()),2)

    # DCF Calculations
    dcf_calc_df, dcf_metrics_dict = calculate_intrinsic_pe(coc/100, roce/100, g/100, g_period, fade_period, gt/100)
    intrinsic_pe = round(float(dcf_metrics_dict["TTM PE"]),2)

    # # Degree of overvaluation
    overvaluation = round(float(calculate_degree_of_overvaluation(current_pe, fy23_pe, intrinsic_pe) * 100),0)

    return symbol, current_pe, fy23_pe, str(median_5yr_roce) + "%", years_data_df[["", "10 Years", "5 Years", "3 Years", "TTM"]].to_dict('records'), round(intrinsic_pe, 2), overvaluation








####################################################################################################################################################################################
# VALUATION FUNCTIONS
####################################################################################################################################################################################

# User inputs are cost of capital, RoCE, growth during high growth period, high growth period (years), fade period (years) and terminal growth rate
# Tax rate is assumed constant at 25%.
import pandas as pd


def calculate_intrinsic_pe(coc, roce, g, g_period, fade_period, gt):
  tax_rate = 0.25
  capital_ending_neg1 = 100

  roce_post_tax = roce * (1-tax_rate)
  reinvestment_rate_1 = g / roce_post_tax
  reinvestment_rate_2 = gt / roce_post_tax

  capital_ending = []
  nopat = []
  ebt = []
  investment = []
  fcf = []
  discount_factor = []
  discount_fcf = []

  earning_g_rate = [g]*g_period
  for i in range(fade_period):
    earning_g_rate.append(earning_g_rate[-1] - ((g-gt)/fade_period) )

  

  for i in range (g_period+1):
    if i == 0:
      nopat.append( capital_ending_neg1 * roce_post_tax )
    else:
      nopat.append( capital_ending[-1] * roce_post_tax)
    
    ebt.append(nopat[-1]/(1-tax_rate))
    investment.append(nopat[-1] * reinvestment_rate_1)
    fcf.append(nopat[-1] - investment[-1])
    discount_factor.append( 1 / ((1+coc)**(i)) )
    discount_fcf.append(fcf[-1] * discount_factor[-1])

    if i == 0:
      capital_ending.append( capital_ending_neg1 + investment[-1])
    else:
      capital_ending.append( capital_ending[-1] + investment[-1])

  for i in range (fade_period):
    nopat.append( capital_ending[-1] * roce_post_tax)
    ebt.append(nopat[-1]/(1-tax_rate))
    investment.append(nopat[-1] * earning_g_rate[i+g_period]  / roce_post_tax)
    fcf.append(nopat[-1] - investment[-1])
    discount_factor.append( 1 / ((1+coc)**(i+g_period+1)) )
    discount_fcf.append(fcf[-1] * discount_factor[-1])
    capital_ending.append( capital_ending[-1] + investment[-1])
  
  earning_g_rate.insert(0,0)
  df = pd.DataFrame({
      "Earnings Growth Rate": earning_g_rate,
      "EBT": ebt, "NOPAT" : nopat,
      "Capital Ending" : capital_ending,
      "Investment" : investment,
      "FCF" : fcf, "Discount Factor": discount_factor, "Discounted FCF" : discount_fcf
  })

  terminal_nopat = nopat[-1] * (1+gt) / (coc - gt)
  terminal_investment = terminal_nopat * reinvestment_rate_2
  terminal_fcf = terminal_nopat - terminal_investment
  terminal_discount_fcf = terminal_fcf * discount_factor[-1]

  metrics_dict = {}
  metrics_dict["intrinsic value"] = df["Discounted FCF"].sum() + terminal_discount_fcf
  metrics_dict["25 yr Exit Multiple"] = terminal_nopat / (nopat[-1] * (1+gt))
  metrics_dict["terminal / total"] = terminal_discount_fcf / metrics_dict["intrinsic value"]
  metrics_dict["TTM PB"] = metrics_dict["intrinsic value"] / df["Capital Ending"].iloc[0]
  metrics_dict["TTM PE"] = metrics_dict["intrinsic value"] / df["NOPAT"].iloc[0]
  metrics_dict["1yr forward PE"] = metrics_dict["intrinsic value"] / df["NOPAT"].iloc[1]

  print(reinvestment_rate_1, reinvestment_rate_2)
  print(earning_g_rate)
  print(earning_g_rate[0+g_period])
  print(df)
  print(terminal_discount_fcf)
  print(metrics_dict)

  return df, metrics_dict


def calculate_degree_of_overvaluation(current_pe, fy23_pe, calculated_intrinsic_pe):
  if current_pe < fy23_pe:
    return (current_pe/calculated_intrinsic_pe) - 1
  else:
    return (fy23_pe/calculated_intrinsic_pe) - 1


# calculate_intrinsic_pe(0.11, 0.2, 0.15, 15, 15, 0.05)
# calculate_intrinsic_pe(0.11, 0.95, 0.15, 15, 15, 0.05)

####################################################################################################################################################################################
# SCRAPING FUNCTIONS
####################################################################################################################################################################################

import requests
from bs4 import BeautifulSoup

def scrape_screener_info(symbol):

  url = "https://www.screener.in/company/"+ symbol.upper() +"/consolidated/"

  try:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # CHECKING IF CONSOLIDATED DATA IS AVAILABLE
    # by checking if PnL table is filled or not
    if not check_consolidated_available(soup):
      try:
        url = "https://www.screener.in/company/"+ symbol.upper() +"/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        print("Using Standalone data, since consolidated numbers are not available")
      except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return -1, "Error"
    
    pnl_section = soup.find("section", id="profit-loss")

    # # TOP RATIOS
    # top_ratios_data = get_top_ratios(soup)

    # print(top_ratios_data)


    # 3, 5, 10 YEAR DATA
    # year_data_tables_data = get_range_tables(pnl_section)

    # print(year_data_tables_data)
    # print(pd.DataFrame(year_data_tables_data))


    # # PNL TABLE
    # pnl_df = get_pnl_table(pnl_section)
    # print(pnl_df)
    # # print(pnl_df.loc["Net Profit", :].iloc[-6:-1])
    # # print(pnl_df.loc["Net Profit", "Mar 2023"])

    # # RATIO TABLE
    # ratio_df = get_ratios(soup)
    # print(ratio_df)
    # print(ratio_df.loc["ROCE %",:].iloc[-7:-2])


    return 200, soup

  except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    return -1, "Error"

# scrape_screener_info("ASIANPAINT")

# print("aa")


def check_consolidated_available(soup):
  section = soup.find("section", id="profit-loss")
  trows = section.find("table", class_="data-table").find("tbody").find_all("tr")
  if len(trows[0].find_all("td")) > 1:
    print(len(trows[0].find_all("td")))
    return True
  else:
    print(len(trows[0].find_all("td")))
    return False


# TOP RATIOS
def get_top_ratios(soup):

  top_ratios_data = {}
  top_ratios_ul = soup.find('ul', id='top-ratios')

  if top_ratios_ul:
    ratios = top_ratios_ul.find_all("li")

    for ratio in ratios:
      ratio_label = ratio.find("span", class_="name").text.strip()
      if ratio_label == "High / Low":
        # ratio_value_list = [span.text.strip().replace(",","") for span in ratio.find_all("span", class_="number")]
        # ratio_value = ' / '.join(ratio_value_list)
        ratio_value_list = ratio.find_all("span", class_="number")
        top_ratios_data["High"] = ratio_value_list[0].text.strip().replace(",","")
        top_ratios_data["Low"] = ratio_value_list[1].text.strip().replace(",","")
      else:
        ratio_value = ratio.find("span", class_="number").text.strip().replace(",","")
        top_ratios_data[ratio_label] = ratio_value

  return top_ratios_data

# 3, 5, 10 YEAR DATA
def get_range_tables(pnl_section):

  year_data_tables_data = []
  year_data_tables = pnl_section.find_all("table", class_ = "ranges-table")

  for table in year_data_tables:
    table_data = {}
    trows = table.find_all("tr")
    header = trows[0].find("th").text.strip()
    table_data[""] = header

    for i in range (1, len(trows)):
      data_points = trows[i].find_all("td")
      label = data_points[0].text.strip().replace(",","").replace(":","")
      value = data_points[1].text.strip().replace(",","").replace(":","")
      table_data[label] = value
    
    year_data_tables_data.append(table_data)
  year_data_tables_data[0][""] = "Sales Growth"
  year_data_tables_data[1][""] = "Profit Growth"

  # for table in year_data_tables:
  #   trows = table.find_all("tr")
  #   header = trows[0].find("th").text.strip()
  #   year_data_tables_data[header] = {}

  #   for i in range (1, len(trows)):
  #     data_points = trows[i].find_all("td")
  #     label = data_points[0].text.strip().replace(",","").replace(":","")
  #     value = data_points[1].text.strip().replace(",","").replace(":","")
  #     year_data_tables_data[header][label] = value

  return year_data_tables_data

# PNL STATEMENT
def get_pnl_table(pnl_section):
  table = pnl_section.find("table", class_="data-table")
  headers = [th.text.strip() for th in table.find('thead').find_all('th')]
  headers[0] = "Particulars"

  data = []
  for row in table.find('tbody').find_all('tr'):
    # row_data = [td.text.strip() for td in row.find_all('td')]
    tds = row.find_all('td')
    row_data = []
    for i in range(len(tds)):
      if i == 0:
        row_data.append(tds[i].text.strip().replace("+", "").strip())
      else:
        data_value = tds[i].text.strip().replace(",", "").replace("%","").strip()
        row_data.append(float(data_value)) if data_value else row_data.append(data_value)

    data.append(row_data)

  df = pd.DataFrame(data, columns=headers)
  df.set_index(df.columns[0], inplace = True)

  return df


# RATIOS
def get_ratios(soup):
  ratio_section = soup.find("section", id="ratios")
  table = ratio_section.find("table", class_="data-table")

  headers = [th.text.strip() for th in table.find('thead').find_all('th')]
  headers[0] = "Particulars"

  data = []
  for row in table.find('tbody').find_all('tr'):
    # row_data = [td.text.strip() for td in row.find_all('td')]
    tds = row.find_all('td')
    row_data = []
    for i in range(len(tds)):
      if i == 0:
        row_data.append(tds[i].text.strip())
      else:
        data_value = tds[i].text.strip().replace(",", "").replace("%","").strip()
        row_data.append(float(data_value)) if data_value else row_data.append(data_value)

    data.append(row_data)

  df = pd.DataFrame(data, columns=headers)
  df.set_index(df.columns[0], inplace = True)
  
  return df
