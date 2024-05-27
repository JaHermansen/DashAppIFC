from dash import html, callback, Output, Input, dcc, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import tempfile
import os
import base64
import traceback
import ifcopenshell
import ifcopenshell.util.element as Element

# Importing the ifchelper functions
def get_objects_data_by_class(file, class_type):
    def add_pset_attributes(psets):
        for pset_name, pset_data in psets.items():
            for property_name in pset_data.keys():
                pset_attributes.add(
                    f"{pset_name}.{property_name}"
                ) if property_name != "id" else None

    objects = file.by_type(class_type)
    objects_data = []
    pset_attributes = set()

    for obj in objects:
        qtos = Element.get_psets(obj, qtos_only=True)
        add_pset_attributes(qtos)
        psets = Element.get_psets(obj, psets_only=True)
        add_pset_attributes(psets)
        objects_data.append(
            {
                "ExpressId": obj.id(),
                "GlobalId": obj.GlobalId,
                "Class": obj.is_a(),
                "PredefinedType": Element.get_predefined_type(obj),
                "Name": obj.Name,
                "Level": Element.get_container(obj).Name
                if Element.get_container(obj)
                else "",
                "Type": Element.get_type(obj).Name
                if Element.get_type(obj)
                else "",
                "QuantitySets": qtos,
                "PropertySets": psets,
            }
        )
    return objects_data, list(pset_attributes)

def get_attribute_value(object_data, attribute):
    if "." not in attribute:
        return object_data[attribute]
    elif "." in attribute:
        pset_name = attribute.split(".", 1)[0]
        prop_name = attribute.split(".", -1)[1]
        if pset_name in object_data["PropertySets"].keys():
            if prop_name in object_data["PropertySets"][pset_name].keys():
                return object_data["PropertySets"][pset_name][prop_name]
            else:
                return None
        elif pset_name in object_data["QuantitySets"].keys():
            if prop_name in object_data["QuantitySets"][pset_name].keys():
                return object_data["QuantitySets"][pset_name][prop_name]
            else:
                return None
        else:
            return None

def create_pandas_dataframe(data, pset_attributes):
    attributes = [
        "ExpressId",
        "GlobalId",
        "Class",
        "PredefinedType",
        "Name",
        "Level",
        "Type",
    ] + pset_attributes
    
    pandas_data = []
    for object_data in data:
        row = []
        for attribute in attributes:
            value = get_attribute_value(object_data, attribute)
            row.append(value)
        pandas_data.append(tuple(row))
    return pd.DataFrame.from_records(pandas_data, columns=attributes)

def get_ifc_pandas(ifc_file):
    data, pset_attributes = get_objects_data_by_class(ifc_file, "IfcBuildingElement")
    return create_pandas_dataframe(data, pset_attributes)


layout = html.Div([
    html.H1("Extract IFC Information"),
    html.Div(id="uploaded-file-info"),
    dcc.Loading(
        id="loading-1",
        type="circle",
        children=html.Div(id='tabs-container', style={'width': '100%', 'overflowX': 'auto'}),
    )
])

@callback(
    Output('uploaded-file-info', 'children'),
    [Input('ifc-data-store', 'data')]
)
def update_uploaded_file_info(ifc_data):
    if ifc_data is not None:
        filename = ifc_data.get('filename')
        name = ifc_data.get('name')

        # Print the name of the loaded file
        print("Loaded File Name:", filename)

        display = html.Div([
            html.H2(f"IFC Project Name: {name}"),
            html.H4(f"Filename: {filename}"),
            # html.H4("Entity Breakdown:"),
            # html.Ul([html.Li(f"{etype}: {count}") for etype, count in entities_info.items()]),
        ])

        return display

    return "No IFC data available."



@callback(
    Output('tabs-container', 'children'),
    [Input('ifc-data-store', 'data')]
)
def update_tabs(ifc_data):
    if ifc_data is None:
        raise PreventUpdate

    try:
        contents = ifc_data.get('file_contents')
        if contents is None:
            raise ValueError("No file contents provided.")

        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ifc") as temp_file:
            temp_file.write(decoded)

            temp_file_path = temp_file.name

        ifc_file = ifcopenshell.open(temp_file_path)
        df = get_ifc_pandas(ifc_file)

        os.remove(temp_file_path)

        # Split DataFrame by Class
        class_dfs = {class_name: df_class for class_name, df_class in df.groupby('Class')}

        # Create tabs
        tabs = []
        for class_name, df_class in class_dfs.items():
            tabs.append(
                dcc.Tab(label=class_name, children=[
                    html.Div([
                        dcc.Tabs([
                            dcc.Tab(label='Data', children=[
                                dash_table.DataTable(
                                    data=df_class.to_dict('records'),
                                    columns=[{'name': i, 'id': i} for i in df_class.columns],
                                    style_table={'overflowX': 'auto'},
                                    style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '300px',
                                                'overflow': 'hidden', 'textOverflow': 'ellipsis'}
                                )
                            ]),
                            dcc.Tab(label='Missing Values', children=[
                                dcc.Graph(
                                    figure=px.bar(
                                        df_class.isna().sum().reset_index(),
                                        x='index',
                                        y=0,
                                        labels={'index': 'Column', 0: 'Missing Values'},
                                        title='Missing Values per Property'
                                    )
                                )
                            ])
                        ])
                    ])
                ], className='custom-tab')
            )

        return dcc.Tabs(children=tabs)
    except Exception as e:
        print("Error parsing contents:", e)
        traceback.print_exc()  # Print full traceback
        return html.Div([
            'There was an error processing this file.'
        ])

