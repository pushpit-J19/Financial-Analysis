import dash
import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table as dt
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Header content
app.layout = html.Div(children = [
    
    dbc.NavbarSimple(
      className = "d-flex  justify-content-start",
      children=[
          # dbc.NavItem(dbc.NavLink("Page 1", href="/")),
          dbc.DropdownMenu(
              label="PAGES",
              children=[
                  dbc.DropdownMenuItem(dcc.Link(page['name'], href=page['relative_path'], style={"text-decoration":"none"}, className = "text-dark ")) for page in dash.page_registry.values()
                  # dbc.DropdownMenuItem(dcc.Link('DCF Valuation', href='/val', style={"text-decoration":"none"}, className = "text-dark ")),
                  # dbc.DropdownMenuItem("Home", href="/"),
                  # dbc.DropdownMenuItem("DCF Valuation", href="/val"),
                  # dbc.DropdownMenuItem(page["name"], href = page["relative-path"]) for page in dash.page_registry.values()
              ],
              nav=True,
              in_navbar=True,
          ),
      ],
      brand="REVERSE DCF",
      brand_href="/",
      color="dark",
      dark=True,
),

    html.Div(
        className = "p-3",
        dash.page_container
    )
    
])

if __name__ == '__main__':
    app.run(debug=False)
