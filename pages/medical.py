"""
Página del Área Médica para UD Atzeneta Analytics
"""
from dash import html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Función para generar datos de prueba para jugadores lesionados
def generate_injured_players_data():
    """Genera datos de ejemplo para la tabla de jugadores lesionados"""
    return [
        {
            'player': 'Carlos Martínez',
            'injury': 'Lesión muscular (cuádriceps)',
            'type': 'Muscular',
            'start_date': '10/03/2024',
            'estimated_return': '24/03/2024',
            'status': 'En Recuperación'
        },
        {
            'player': 'David Sánchez',
            'injury': 'Esguince de tobillo',
            'type': 'Articular',
            'start_date': '05/03/2024',
            'estimated_return': '20/03/2024',
            'status': 'En Recuperación'
        },
        {
            'player': 'Alejandro Rodríguez',
            'injury': 'Contusión en rodilla',
            'type': 'Contusión',
            'start_date': '12/03/2024',
            'estimated_return': '15/03/2024',
            'status': 'Readaptación'
        }
    ]

# Función para crear el gráfico de distribución de lesiones
def create_injury_distribution_graph():
    """Crea un gráfico circular de distribución de lesiones por tipo"""
    injury_data = {
        'Tipo': ['Muscular', 'Articular', 'Ósea', 'Contusión', 'Otra'],
        'Cantidad': [8, 4, 2, 5, 1]
    }
    
    df = pd.DataFrame(injury_data)
    
    fig = px.pie(
        df, 
        values='Cantidad', 
        names='Tipo', 
        title='Distribución por Tipo de Lesión',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=40, b=60)
    )
    
    return fig

# Función para crear el gráfico de tiempo medio de recuperación
def create_recovery_time_graph():
    """Crea un gráfico de barras con el tiempo medio de recuperación por tipo de lesión"""
    recovery_data = {
        'Tipo': ['Muscular', 'Articular', 'Ósea', 'Contusión', 'Otra'],
        'Días': [14, 21, 35, 7, 10]
    }
    
    df = pd.DataFrame(recovery_data)
    
    fig = px.bar(
        df, 
        x='Tipo', 
        y='Días',
        title='Tiempo Medio de Recuperación por Tipo de Lesión',
        color='Días',
        text_auto=True,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=12),
        xaxis_title="Tipo de Lesión",
        yaxis_title="Días de Recuperación (Promedio)",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

# Función para crear el mapa de calor de lesiones en campo de fútbol
def create_injury_heatmap():
    """Crea un mapa de calor de lesiones en un campo de fútbol"""
    # Crear un campo de fútbol
    fig = go.Figure()
    
    # Dimensiones del campo (en metros)
    field_length = 105
    field_width = 68
    
    # Dibujar el campo base
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=field_length, y1=field_width,
        line=dict(color="white"),
        fillcolor="green",
    )
    
    # Dibujar líneas centrales
    fig.add_shape(
        type="rect", x0=0, y0=0, x1=field_length, y1=field_width,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    fig.add_shape(
        type="line", x0=field_length/2, y0=0, x1=field_length/2, y1=field_width,
        line=dict(color="white", width=2)
    )
    fig.add_shape(
        type="circle", x0=field_length/2-9.15, y0=field_width/2-9.15, x1=field_length/2+9.15, y1=field_width/2+9.15,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Áreas
    # Área grande izquierda
    fig.add_shape(
        type="rect", x0=0, y0=field_width/2-20.16, x1=16.5, y1=field_width/2+20.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    # Área pequeña izquierda
    fig.add_shape(
        type="rect", x0=0, y0=field_width/2-9.16, x1=5.5, y1=field_width/2+9.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    # Área grande derecha
    fig.add_shape(
        type="rect", x0=field_length-16.5, y0=field_width/2-20.16, x1=field_length, y1=field_width/2+20.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    # Área pequeña derecha
    fig.add_shape(
        type="rect", x0=field_length-5.5, y0=field_width/2-9.16, x1=field_length, y1=field_width/2+9.16,
        line=dict(color="white", width=2),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Datos simulados de lesiones (posición x, posición y, intensidad)
    np.random.seed(42)  # Para reproducibilidad
    num_points = 50
    x = np.random.uniform(0, field_length, num_points)
    y = np.random.uniform(0, field_width, num_points)
    intensity = np.random.uniform(1, 10, num_points)
    
    # Agregar mapa de calor
    fig.add_trace(go.Histogram2dContour(
        x=x, y=y, z=intensity,
        colorscale='Hot',
        reversescale=True,
        showscale=True,
        opacity=0.8,
        colorbar=dict(
            title="Intensidad<br>de Lesiones",
            titleside="right",
            thickness=15,
            len=0.6,
            y=0.5
        )
    ))
    
    # Configuración del layout
    fig.update_layout(
        title="Mapa de Calor de Lesiones",
        width=700,
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            range=[0, field_length],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, field_width],
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        ),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

# Función para crear el gráfico de evolución de lesiones
def create_injury_evolution_graph():
    """Crea un gráfico de línea con la evolución de lesiones por mes"""
    # Datos de ejemplo
    months = ['Sep', 'Oct', 'Nov', 'Dic', 'Ene', 'Feb', 'Mar']
    
    evolution_data = {
        'Mes': months,
        'Lesiones': [2, 3, 5, 6, 4, 3, 3],
        'Días Perdidos': [14, 21, 35, 42, 28, 18, 21]
    }
    
    df = pd.DataFrame(evolution_data)
    
    # Crear figura con dos ejes Y
    fig = go.Figure()
    
    # Añadir línea para número de lesiones
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Lesiones'],
        name='Número de Lesiones',
        line=dict(color='#1f77b4', width=3),
        mode='lines+markers'
    ))
    
    # Añadir línea para días perdidos
    fig.add_trace(go.Scatter(
        x=df['Mes'],
        y=df['Días Perdidos'],
        name='Días Perdidos',
        line=dict(color='#ff7f0e', width=3, dash='dot'),
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # Actualizar layout con dos ejes Y
    fig.update_layout(
        title='Evolución de Lesiones durante la Temporada',
        xaxis=dict(
            title='Mes',
            showgrid=True
        ),
        yaxis=dict(
            title='Número de Lesiones',
            showgrid=True,
            range=[0, max(df['Lesiones']) + 2]
        ),
        yaxis2=dict(
            title='Días Perdidos',
            titlefont=dict(color='#ff7f0e'),
            tickfont=dict(color='#ff7f0e'),
            anchor="x",
            overlaying="y",
            side="right",
            range=[0, max(df['Días Perdidos']) + 10]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=20, r=60, t=40, b=20)
    )
    
    return fig

def medical_layout():
    """
    Crea el layout para la página del área médica
    """
    return dbc.Container([
        # Título y descripción
        dbc.Row([
            dbc.Col([
                html.H1("Área Médica", className="text-center my-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "Seguimiento médico de los jugadores, control de lesiones, y estadísticas de salud "
                            "del equipo UD Atzeneta."
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Filtros
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Filtros", className="m-0")),
                    dbc.CardBody([
                        dbc.Row([
                            # Filtro de jugador
                            dbc.Col([
                                html.Label("Jugador"),
                                dcc.Dropdown(
                                    id='player-filter',
                                    options=[
                                        {'label': 'Todos los jugadores', 'value': 'all'},
                                        {'label': 'Carlos Martínez', 'value': 'carlos'},
                                        {'label': 'David Sánchez', 'value': 'david'},
                                        {'label': 'Alejandro Rodríguez', 'value': 'alejandro'},
                                        {'label': 'Miguel Torres', 'value': 'miguel'},
                                        {'label': 'Javier López', 'value': 'javier'},
                                    ],
                                    value='all',
                                    clearable=False
                                )
                            ], md=6),
                            
                            # Filtro de tipo de lesión
                            dbc.Col([
                                html.Label("Tipo de Lesión"),
                                dcc.Dropdown(
                                    id='injury-type-filter',
                                    options=[
                                        {'label': 'Todas las lesiones', 'value': 'all'},
                                        {'label': 'Muscular', 'value': 'muscular'},
                                        {'label': 'Articular', 'value': 'articular'},
                                        {'label': 'Ósea', 'value': 'osea'},
                                        {'label': 'Contusión', 'value': 'contusion'},
                                        {'label': 'Otra', 'value': 'otra'}
                                    ],
                                    value='all',
                                    clearable=False
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        # Botón para actualizar la visualización
                        dbc.Button(
                            "Actualizar Datos", 
                            id="update-medical-btn", 
                            color="primary", 
                            className="mt-2"
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Tarjetas de resumen
        dbc.Row([
            # Lesiones activas
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2("3", id="active-injuries-count", className="text-center"),
                        html.P("Lesiones Activas", className="text-center")
                    ], className="text-danger")
                ], className="mb-4 text-center")
            ], md=4),
            
            # Días de baja
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2("47", id="days-lost-count", className="text-center"),
                        html.P("Días de Baja", className="text-center")
                    ], className="text-warning")
                ], className="mb-4 text-center")
            ], md=4),
            
            # Tiempo promedio de recuperación
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2("12.5", id="avg-recovery-time", className="text-center"),
                        html.P("Días Promedio de Recuperación", className="text-center")
                    ], className="text-primary")
                ], className="mb-4 text-center")
            ], md=4)
        ]),
        
        # Gráficos médicos - Fila 1
        dbc.Row([
            # Gráfico de distribución de lesiones
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Distribución de Lesiones", className="m-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            id='injury-distribution-graph',
                            figure=create_injury_distribution_graph()
                        )
                    ])
                ], className="mb-4")
            ], md=6),
            
            # Gráfico de tiempo medio de recuperación
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Tiempo de Recuperación", className="m-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            id='recovery-time-graph',
                            figure=create_recovery_time_graph()
                        )
                    ])
                ], className="mb-4")
            ], md=6)
        ]),
        
        # Tabla de jugadores lesionados
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Jugadores Lesionados", className="m-0")),
                    dbc.CardBody([
                        dash_table.DataTable(
                            id='injured-players-table',
                            columns=[
                                {'name': 'Jugador', 'id': 'player'},
                                {'name': 'Lesión', 'id': 'injury'},
                                {'name': 'Tipo', 'id': 'type'},
                                {'name': 'Fecha Inicio', 'id': 'start_date'},
                                {'name': 'Retorno Estimado', 'id': 'estimated_return'},
                                {'name': 'Estado', 'id': 'status'}
                            ],
                            data=generate_injured_players_data(),
                            style_table={'overflowX': 'auto'},
                            style_header={
                                'backgroundColor': 'rgb(30, 67, 137)',
                                'color': 'white',
                                'fontWeight': 'bold',
                                'textAlign': 'center',
                                'padding': '10px 5px'
                            },
                            style_cell={
                                'textAlign': 'center',
                                'padding': '10px 5px',
                                'minWidth': '100px'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{status} = "En Recuperación"'},
                                    'backgroundColor': 'rgba(255, 235, 156, 0.5)',
                                    'color': '#856404'
                                },
                                {
                                    'if': {'filter_query': '{status} = "Evaluación"'},
                                    'backgroundColor': 'rgba(254, 216, 214, 0.5)',
                                    'color': '#721c24'
                                },
                                {
                                    'if': {'filter_query': '{status} = "Readaptación"'},
                                    'backgroundColor': 'rgba(209, 236, 241, 0.5)',
                                    'color': '#0c5460'
                                }
                            ]
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Gráficos médicos - Fila 2
        dbc.Row([
            # Campo de fútbol con mapa de calor de lesiones
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Mapa de Lesiones", className="m-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            id='injury-heatmap',
                            figure=create_injury_heatmap()
                        )
                    ])
                ], className="mb-4")
            ], md=6),
            
            # Gráfico de evolución de lesiones
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Evolución Temporal", className="m-0")),
                    dbc.CardBody([
                        dcc.Graph(
                            id='injury-evolution-graph',
                            figure=create_injury_evolution_graph()
                        )
                    ])
                ], className="mb-4")
            ], md=6)
        ]),
        
        # Botón para exportar informe
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    [
                        html.I(className="fa fa-file-pdf-o me-2"),
                        "Exportar Informe Médico"
                    ], 
                    id="export-medical-btn", 
                    color="success", 
                    className="float-end mb-4"
                )
            ])
        ])
    ], fluid=True)

def register_medical_callbacks(app):
    """
    Registra los callbacks para la página médica
    """
    # Callback para actualizar los datos médicos
    @app.callback(
        [Output('active-injuries-count', 'children'),
         Output('days-lost-count', 'children'),
         Output('avg-recovery-time', 'children'),
         Output('injured-players-table', 'data')],
        [Input('update-medical-btn', 'n_clicks')],
        [State('player-filter', 'value'),
         State('injury-type-filter', 'value')]
    )
    def update_medical_data(n_clicks, player, injury_type):
        """
        Actualiza los datos médicos según los filtros seleccionados
        """
        # Datos simulados - en una app real, estos vendrían de la base de datos
        data = generate_injured_players_data()
        
        # Filtrar por jugador si es necesario
        if player != 'all':
            # En una app real, haríamos el filtrado adecuado
            # Para este ejemplo, solo cambiamos el contador
            active_injuries = len(data) - 1
            days_lost = 35
            avg_recovery = 11.3
        else:
            active_injuries = len(data)
            days_lost = 47
            avg_recovery = 12.5
        
        # Filtrar por tipo de lesión si es necesario
        if injury_type != 'all':
            # Filtrar los datos de la tabla
            filtered_data = [row for row in data if row['type'].lower() == injury_type.lower()]
            return active_injuries, days_lost, f"{avg_recovery}", filtered_data
        
        return active_injuries, days_lost, f"{avg_recovery}", data

    # Callback para el botón de exportar informe médico
    @app.callback(
        Output('export-medical-btn', 'n_clicks'),
        Input('export-medical-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def export_medical_report(n_clicks):
        """
        Genera un informe médico en PDF (simulado)
        """
        if n_clicks:
            # En una app real, aquí generaríamos el PDF
            # Para este ejemplo, simplemente mostramos un mensaje en la consola
            print("Generando informe médico en PDF...")
            # Y no hacemos nada más, solo reiniciamos el contador de clics
            return 0
        return dash.no_update