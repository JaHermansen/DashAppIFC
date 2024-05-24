import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_auth
import flask
import base64

# Import layouts from separate files
from pages import home, page1, page2


# Define valid username-password pairs
VALID_USERNAME_PASSWORD_PAIRS = {
    'JH': '1234'
}

# Create the Flask server instance and set a secret key for session management
server = flask.Flask(__name__)
server.secret_key = 'VerySecret'  # Replace with a strong random string

# Initialize the Dash app with the Flask server
app = dash.Dash(
    server=server,
    external_stylesheets=[dbc.themes.LUX],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    suppress_callback_exceptions=True  # Add this line to suppress the exception
)

# Initialize BasicAuth
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

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

# Layout for the entire application
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    content,
])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/ExtractNestedProperties":
        return page1.layout
    elif pathname == "/BatchCheck":
        return page2.layout
    else:
        return html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ],
            className="p-3 bg-light rounded-3",
        )


@app.callback(
    Output("collapse", "is_open"),
    [Input("toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# Callback to handle file uploads
@app.callback(
    Output('upload-output', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        # Process the uploaded file here
        return f'File {filename} uploaded successfully.'
    else:
        return ''


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
