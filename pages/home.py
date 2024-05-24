from dash import html, dcc
from dash.dependencies import Input, Output
from app import app

# Define the layout for the home page
layout = html.Div([
    html.H1("Welcome to the Home Page"),
    html.P("This is the landing page of your Dash app."),
    
    # Upload component for users to upload files
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow only one file to be uploaded
        multiple=False
    ),
    
    # Text box to display the name of the uploaded file
    dcc.Input(id='file-name-output', type='text', value='', readOnly=True)
])

# Callback to display the name of the uploaded file
@app.callback(
    Output('file-name-output', 'value'),
    [Input('upload-data', 'filename')]
)
def display_uploaded_file_name(filename):
    return filename or ''  # If filename is None, return an empty string
