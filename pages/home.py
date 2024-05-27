from dash import html, dcc, callback, register_page
from dash.dependencies import Input, Output, State
import dash
import base64
import ifcopenshell
from datetime import datetime
import tempfile
import os

dash.register_page(
    __name__,
    path='/',
    title='Home'
)

# Define the layout for the home page
layout = html.Div([
    html.H1("Welcome to the data manager"),
    html.P("Upload your IFC file and start extracting properties"),
    
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
        # Allow only .ifc files to be uploaded
        accept='.ifc',
        multiple=False
    ),
    
    # Div to display the overview of the uploaded file with a loading spinner
    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=html.Div(id='file-overview')
    )
])

# Callback to process the uploaded file and display an overview
@callback(
    Output('file-overview', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_file:
            temp_file.write(decoded)
            temp_filepath = temp_file.name

        # Open and parse the IFC file
        ifc_file = ifcopenshell.open(temp_filepath)

        # Extract information
        project = ifc_file.by_type('IfcProject')[0]
        name = project.Name
        # creation_date = datetime.fromtimestamp(ifc_file.header.file_description.creation_date().timestamp())
        # entities_count = len(ifc_file)

        # Additional information
        entities_info = {}
        for entity in ifc_file.by_type('IfcRoot'):
            entity_type = entity.is_a()
            if entity_type not in entities_info:
                entities_info[entity_type] = 0
            entities_info[entity_type] += 1

        # Format the output
        overview = html.Div([
            html.H3(f"Overview of {filename}"),
            html.P(f"Name: {name}"),
            # html.P(f"Creation Date: {creation_date}"),
            # html.P(f"Total Number of Entities: {entities_count}"),
            html.H4("Entity Breakdown:"),
            html.Ul([html.Li(f"{etype}: {count}") for etype, count in entities_info.items()]),
        ])

        # Clean up the temporary file
        os.remove(temp_filepath)

        return overview

    return "No file uploaded yet."
