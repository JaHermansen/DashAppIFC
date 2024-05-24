from dash import Dash, dcc, html, dash_table, Input, Output, State, ctx
import dash_daq as daq
import dash_loading_spinners
import base64
import io
import pandas as pd
import traceback
from openpyxl import Workbook
from openpyxl.styles import PatternFill
import ifcopenshell
import ifcopenshell.util.element as Element
import ifcopenshell.api
from datetime import datetime
import tempfile
import os
import plotly.express as px

from app import app



layout = html.P("Oh cool, this is page 1!")
