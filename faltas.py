"""
Faltas - UD Atzeneta
Página de análisis de faltas del equipo
"""
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_login import login_required, current_user

# Definición del layout de la página de faltas
def faltas_layout():
    return html.Div([
        dbc.Container([
            # Título de la página
            html.H2("Análisis de Faltas", className="mb-4 mt-4"),
            
            # Contenido de la página (vacío por ahora)
            html.Div(id="faltas-content-placeholder")
        ], fluid=True)
    ])

# Registrar callbacks
def register_faltas_callbacks(app):
    # Sin callbacks por ahora
    pass