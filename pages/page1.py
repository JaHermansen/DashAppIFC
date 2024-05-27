from dash import html, register_page
import dash

dash.register_page(
    __name__,
    path='/ExtractNestedProperties',
    title='Extract IFC Information'
)

layout = html.P("Oh cool, this is page 1!")
