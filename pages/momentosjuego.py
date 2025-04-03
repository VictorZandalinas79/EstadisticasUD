"""
Momentos de Juego - UD Atzeneta
Página de análisis de momentos de juego del equipo
"""
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_login import login_required, current_user

# Definición del layout de la página de momentos de juego
def momentosjuego_layout():
    return html.Div([
        dbc.Container([
            # Título de la página
            html.H2("Análisis de Momentos de Juego", className="mb-4 mt-4"),
            
            # Contenido de la página (vacío por ahora)
            html.Div(id="momentosjuego-content-placeholder")
        ], fluid=True)
    ])

# Registrar callbacks
def register_momentosjuego_callbacks(app):
    # Sin callbacks por ahora
    pass