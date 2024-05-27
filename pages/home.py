from dash import html, dcc, callback, register_page
from dash.dependencies import Input, Output, State
import base64
import ifcopenshell
import tempfile
import os

register_page(
    __name__,
    path='/',
    title='Home'
)

layout = html.Div([
    html.H1("Welcome to the data manager"),
    html.P("Upload your IFC file and start extracting properties"),
    
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
        accept='.ifc',
        multiple=False
    ),
    
    dcc.Store(id='stored-file', storage_type='session'),

    dcc.Loading(
        id="loading-spinner",
        type="circle",
        children=html.Div(id='file-overview')
    )
])

@callback(
    Output('stored-file', 'data'),
    Output('ifc-data-store', 'data'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def store_uploaded_file(contents, filename):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_file:
            temp_file.write(decoded)
            temp_filepath = temp_file.name

        ifc_file = ifcopenshell.open(temp_filepath)
        project = ifc_file.by_type('IfcProject')[0]
        name = project.Name

        entities_info = {}
        for entity in ifc_file.by_type('IfcRoot'):
            entity_type = entity.is_a()
            if entity_type not in entities_info:
                entities_info[entity_type] = 0
            entities_info[entity_type] += 1

        overview = html.Div([
            html.H3(f"Overview of {filename}"),
            html.P(f"Name: {name}"),
            html.H4("Entity Breakdown:"),
            html.Ul([html.Li(f"{etype}: {count}") for etype, count in entities_info.items()]),
        ])

        os.remove(temp_filepath)

        ifc_data = {
            'filename': filename,
            'name': name,
            'entities_info': entities_info
        }

        return {'contents': contents, 'filename': filename}, ifc_data

    return None, None

@callback(
    Output('file-overview', 'children'),
    [Input('stored-file', 'data')]
)
def update_output(stored_file):
    if stored_file is not None:
        contents = stored_file['contents']
        filename = stored_file['filename']
        
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_file:
            temp_file.write(decoded)
            temp_filepath = temp_file.name

        ifc_file = ifcopenshell.open(temp_filepath)
        project = ifc_file.by_type('IfcProject')[0]
        name = project.Name

        entities_info = {}
        for entity in ifc_file.by_type('IfcRoot'):
            entity_type = entity.is_a()
            if entity_type not in entities_info:
                entities_info[entity_type] = 0
            entities_info[entity_type] += 1

        overview = html.Div([
            html.H3(f"Overview of {filename}"),
            html.P(f"Name: {name}"),
            html.H4("Entity Breakdown:"),
            html.Ul([html.Li(f"{etype}: {count}") for etype, count in entities_info.items()]),
        ])

        os.remove(temp_filepath)
        return overview

    return "No file uploaded yet."
