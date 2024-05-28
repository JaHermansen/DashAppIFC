import pandas as pd
from dash import html, callback, Output, Input, dcc, dash_table, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import tempfile
import os
import base64
import ifcopenshell
import ifcopenshell.util.element as Element
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import io
from datetime import datetime


layout = html.Div([
    html.H1("Extract IFC Information"),
    html.Div(id="uploaded-file-info"),
    dcc.Loading(
        id="loading-1",
        type="circle",
        children=html.Div(id='tabs-container', style={'width': '100%', 'overflowX': 'auto'}),
    ),
    html.Button("Download Excel", id="btn-download"),
    dcc.Download(id="download-excel"),
    dcc.Store(id='stored-data')
])

@callback(
    Output('uploaded-file-info', 'children'),
    Input('ifc-data-store', 'data')
)
def update_uploaded_file_info(ifc_data):
    if ifc_data is not None:
        filename = ifc_data.get('filename')
        name = ifc_data.get('name')

        display = html.Div([
            html.H2(f"IFC Project Name: {name}"),
            html.H4(f"Filename: {filename}")
        ])

        return display

    return "No IFC data available."

def get_ifc_pandas(ifc_file):
    def get_objects_data_by_class(file, class_type):
        def add_pset_attributes(psets):
            for pset_name, pset_data in psets.items():
                for property_name in pset_data.keys():
                    pset_attributes.add(f"{pset_name}.{property_name}") if property_name != "id" else None

        objects = file.by_type(class_type)
        objects_data = []
        pset_attributes = set()

        for obj in objects:
            qtos = Element.get_psets(obj, qtos_only=True)
            add_pset_attributes(qtos)
            psets = Element.get_psets(obj, psets_only=True)
            add_pset_attributes(psets)
            objects_data.append({
                "ExpressId": obj.id(),
                "GlobalId": obj.GlobalId,
                "Class": obj.is_a(),
                "PredefinedType": Element.get_predefined_type(obj),
                "Name": obj.Name,
                "Level": Element.get_container(obj).Name if Element.get_container(obj) else "",
                "Type": Element.get_type(obj).Name if Element.get_type(obj) else "",
                "QuantitySets": qtos,
                "PropertySets": psets,
            })
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

    data, pset_attributes = get_objects_data_by_class(ifc_file, "IfcBuildingElement")
    return create_pandas_dataframe(data, pset_attributes)

@callback(
    Output('tabs-container', 'children'),
    Input('ifc-data-store', 'data')
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

        return dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'minWidth': '100px', 'width': '100px', 'maxWidth': '300px',
                        'overflow': 'hidden', 'textOverflow': 'ellipsis'}
        )

    except Exception as e:
        print("Error parsing contents:", e)



@callback(
    Output('export-to-excel', 'disabled'),
    Input('tabs-container', 'children')
)
def enable_export_button(tabs):
    return False if tabs else True

@callback(
    Output("download-excel", "data"),
    Input("btn-download", "n_clicks"),
    State("tabs-container", "children"),
    prevent_initial_call=True
)
def download_excel(n_clicks, data_table):
    if data_table:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            data = data_table.get('props', {}).get('data')
            columns = [col['name'] for col in data_table.get('props', {}).get('columns', [])]
            if data is not None and columns:
                df = pd.DataFrame(data, columns=columns)
                df.fillna("", inplace=True)  # Replace "N/A" with any value
                class_values = df['Class'].unique()
                for class_value in class_values:
                    class_df = df[df['Class'] == class_value]
                    class_df.to_excel(writer, index=False, sheet_name=class_value)
                    
        output.seek(0)
        today_date = datetime.now().strftime('%Y-%m-%d')
        new_filename = f"Extracted_IFC_Data_{today_date}.xlsx"
        return dcc.send_bytes(output.getvalue(), new_filename)
    return None