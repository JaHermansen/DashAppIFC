import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import dash_auth
import flask
from flask import Flask

server = Flask(__name__)

VALID_USERNAME_PASSWORD_PAIRS = {
    'JH': '1234'
}

server = flask.Flask(__name__)
server.secret_key = 'VerySecret'

app = dash.Dash(
    server=server,
    use_pages=True,
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True,
    title='Data Manager'
)

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

from pages import home_layout, page1_layout, page2_layout

sidebar_header = dbc.Row(
    [
        dbc.Col(html.H2("DATA MANAGER", className="display-6", id="title")),
        dbc.Col(
            html.Button(
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                style={
                    "color": "rgba(0,0,0,.5)",
                    "border-color": "rgba(0,0,0,.1)",
                },
                id="toggle",
            ),
            width="auto",
            align="center",
        ),
    ],
    align="center",
)

sidebar = html.Div(
    [
        sidebar_header,
        html.Div(
            [
                html.Hr(),
                html.P(
                    "A tool to extract nested information in IFC models",
                    className="lead",
                ),
            ],
            id="blurb",
        ),
        dbc.Collapse(
            dbc.Nav(
                [
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Extract IFC information", href="/ExtractNestedProperties", active="exact"),
                    dbc.NavLink("Batch check IFC models", href="/BatchCheck", active="exact"),
                ],
                vertical=True,
                pills=True,
            ),
            id="collapse",
        ),
    ],
    id="sidebar",
    style={"background-image": "url('/assets/ribbon2.jpg')",
           "background-size": "cover",
           "background-repeat": "no-repeat",
           "background-position": "center"}
)

content = html.Div(id="page-content")

app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id='ifc-data-store', storage_type='memory'),  # Change storage_type to 'memory'
    sidebar,
    content,
])

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home_layout
    elif pathname == "/ExtractNestedProperties":
        return page1_layout
    elif pathname == "/BatchCheck":
        return page2_layout
    else:
        return html.Div("404: Not found")

if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
