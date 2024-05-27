from dash import html, register_page
import dash 
dash.register_page(
    __name__,
    path='/BatchCheck',
    title='Batch Check IFC Models'
)

layout = html.P("Oh cool, this is page 2!")
