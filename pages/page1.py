from dash import html, register_page, callback, Output, Input
import dash

dash.register_page(
    __name__,
    path='/ExtractNestedProperties',
    title='Extract IFC Information'
)

# Define the layout for page 1
layout = html.Div([
    html.H1("Extract IFC Information"),
    html.P(id="uploaded-file-info")
])

# Callback to update the uploaded file information
@callback(
    Output('uploaded-file-info', 'children'),
    [Input('stored-file', 'data')]
)
def update_uploaded_file_info(stored_file):
    if stored_file and 'filename' in stored_file:
        filename = stored_file['filename']
        return f"Uploaded File: {filename}"
    return "No file uploaded yet."
