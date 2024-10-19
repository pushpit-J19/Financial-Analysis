import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name = "Home", external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdn.jsdelivr.net/npm/bootstrap@4.4.1/dist/css/bootstrap.min.css'])

layout = html.Div(
    # style = {"padding":"5%"}, 
    className = "px-5 py-2", 
    children = [
        html.Div('This site provides interactive tools to valuate and analyze stocks through Reverse DCF model. Check the navigation bar for more.'),
    
        html.Div(children = [
              html.Footer(
                  className = "d-flex flex-wrap justify-content-between align-items-center py-3 my-4 border-top", 
                  style = {
                      "position": "absolute", "bottom": "0", "left": "0",
                      "width": "100%",
                      "padding-left": "5%", "padding-right": "5%",
                  },
                  children = [
                      html.P(className = "col-md-4 d-flex align-items-center", children = [
                          html.Span(className = "mb-3 mb-md-0 text-body-secondary", children = [
                              "Created by: Pushpit Jain", 
                              html.Br(), 
                              html.Span(children = ["Inspired by: ", html.A("Ambit", href = "https://reversedcf-fb0dd87970ce.herokuapp.com/")])
                                ]),
                          # html.Span(className = "mb-4 mb-md-4 text-body-secondary", children = ["Inspired: ", html.A("Ambit", href = "https://reversedcf-fb0dd87970ce.herokuapp.com/")]),
                      ]),
                      html.Div(className = "col-md-4 d-flex align-items-center justify-content-end", children = [
                          html.Span(className = "mb-3 mb-md-0 text-body-secondary", children = ["Source Code: "]),
                          html.A(html.Img(src = "https://github.githubassets.com/assets/GitHub-Mark-ea2971cee799.png", height = "40"), href = "https://github.com/pushpit-J19/Financial-Analysis/tree/main")
                      ]),
        
                  ]),
              
          ])
    
])
