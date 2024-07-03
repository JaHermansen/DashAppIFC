from dash import html, register_page
import dash 
dash.register_page(
    __name__,
    path='/BatchCheck',
    title='Batch Check IFC Models (WIP)'
)

layout = html.P("Work in progress...")
