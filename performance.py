"""
Página de análisis de rendimiento
"""
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.database import get_all_matches_data

def performance_layout():
    """
    Crea el layout para la página de análisis de rendimiento
    """
    return dbc.Container([
        # Título y descripción
        dbc.Row([
            dbc.Col([
                html.H1("Análisis de Rendimiento", className="text-center my-4"),
                dbc.Card([
                    dbc.CardBody([
                        html.P(
                            "Análisis detallado de las métricas de rendimiento del equipo UD Atzeneta. "
                            "Utilice los filtros para personalizar la visualización."
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
                            # Filtro de tipo de partido
                            dbc.Col([
                                html.Label("Tipo de Partido"),
                                dcc.Dropdown(
                                    id='match-type-filter',
                                    options=[
                                        {'label': 'Todos', 'value': 'all'},
                                        {'label': 'Liga', 'value': 'Liga'},
                                        {'label': 'Copa', 'value': 'Copa'}
                                    ],
                                    value='all',
                                    clearable=False
                                )
                            ], md=6),
                            
                            # Filtro de métrica
                            dbc.Col([
                                html.Label("Métrica"),
                                dcc.Dropdown(
                                    id='metric-filter',
                                    options=[
                                        {'label': 'Balones Largos Propios (BLP %)', 'value': 'blp_percentage'},
                                        {'label': 'Balones Largos Rivales (BLR %)', 'value': 'blr_percentage'},
                                        {'label': 'Presión Tras Pérdida (PTP %)', 'value': 'ptp_percentage'},
                                        {'label': 'Retornos (RET %)', 'value': 'ret_percentage'},
                                        {'label': 'Ocupación Centros (OC %)', 'value': 'oc_percentage'},
                                        {'label': 'Vigilancias Defensivas (VD %)', 'value': 'vd_percentage'},
                                        {'label': 'Ocasiones Creadas', 'value': 'ocas_atz'},
                                        {'label': 'Ocasiones Recibidas', 'value': 'ocas_rival'},
                                        {'label': 'Diferencia Ocasiones', 'value': 'dif_ocas'}
                                    ],
                                    value='blp_percentage',
                                    clearable=False
                                )
                            ], md=6)
                        ], className="mb-3"),
                        
                        # Botón para actualizar gráficos
                        dbc.Button(
                            "Actualizar Gráficos", 
                            id="update-graphs-btn", 
                            color="primary", 
                            className="mt-2"
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Gráficos de rendimiento
        dbc.Row([
            # Gráfico de evolución
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Evolución de la Métrica", className="m-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-evolution-graph",
                            type="circle",
                            children=dcc.Graph(id='evolution-graph', config={'displayModeBar': True})
                        )
                    ])
                ], className="mb-4")
            ], md=12, lg=8),
            
            # Tarjetas de resumen
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Resumen", className="m-0")),
                    dbc.CardBody([
                        # Valor promedio
                        html.Div([
                            html.H6("Promedio", className="text-muted"),
                            html.H3(id="avg-value", className="mb-0")
                        ], className="mb-4"),
                        
                        # Mejor valor
                        html.Div([
                            html.H6("Mejor Valor", className="text-muted"),
                            html.H3(id="best-value", className="mb-0 text-success"),
                            html.P(id="best-match", className="text-small")
                        ], className="mb-4"),
                        
                        # Peor valor
                        html.Div([
                            html.H6("Peor Valor", className="text-muted"),
                            html.H3(id="worst-value", className="mb-0 text-danger"),
                            html.P(id="worst-match", className="text-small")
                        ], className="mb-4"),
                        
                        # Tendencia
                        html.Div([
                            html.H6("Tendencia Actual", className="text-muted"),
                            html.Div(id="trend-indicator")
                        ])
                    ])
                ], className="mb-4")
            ], md=12, lg=4)
        ]),
        
        # Gráfico comparativo y pastel
        dbc.Row([
            # Gráfico comparativo Liga vs Copa
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Comparativa Liga vs Copa", className="m-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-comparative-graph",
                            type="circle",
                            children=dcc.Graph(id='comparative-graph', config={'displayModeBar': True})
                        )
                    ])
                ], className="mb-4")
            ], md=12, lg=6),
            
            # Gráfico de distribución
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Distribución por Rango", className="m-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-distribution-graph",
                            type="circle",
                            children=dcc.Graph(id='distribution-graph', config={'displayModeBar': True})
                        )
                    ])
                ], className="mb-4")
            ], md=12, lg=6)
        ]),
        
        # Botón para exportar informe
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Exportar Informe de Rendimiento", 
                    id="export-performance-btn", 
                    color="success", 
                    className="float-end mb-4"
                )
            ])
        ])
    ], fluid=True)

def register_performance_callbacks(app):
    """
    Registra los callbacks para la página de rendimiento
    """
    # Callback para actualizar los gráficos
    @app.callback(
        [Output('evolution-graph', 'figure'),
         Output('comparative-graph', 'figure'),
         Output('distribution-graph', 'figure'),
         Output('avg-value', 'children'),
         Output('best-value', 'children'),
         Output('worst-value', 'children'),
         Output('best-match', 'children'),
         Output('worst-match', 'children'),
         Output('trend-indicator', 'children')],
        [Input('update-graphs-btn', 'n_clicks')],
        [State('match-type-filter', 'value'),
         State('metric-filter', 'value')]
    )
    def update_performance_graphs(n_clicks, match_type, metric):
        """
        Actualiza todos los gráficos basados en los filtros seleccionados
        """
        # Obtener los datos
        data = get_all_matches_data()
        
        if not data:
            # Retornar figuras vacías si no hay datos
            empty_fig = px.line(title="No hay datos disponibles")
            return empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Convertir a DataFrame
        df = pd.DataFrame(data)
        
        # Filtrar por tipo de partido si es necesario
        if match_type != 'all':
            df = df[df['match_type'] == match_type]
        
        if df.empty:
            # Retornar figuras vacías si el DataFrame está vacío después del filtrado
            empty_fig = px.line(title="No hay datos disponibles para los filtros seleccionados")
            return empty_fig, empty_fig, empty_fig, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"
        
        # Preparar los datos para los gráficos
        df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')
        df = df.sort_values('fecha_parsed')
        
        # Definir nombre de la métrica para mostrar
        metric_names = {
            'blp_percentage': 'Balones Largos Propios (%)',
            'blr_percentage': 'Balones Largos Rivales (%)',
            'ptp_percentage': 'Presión Tras Pérdida (%)',
            'ret_percentage': 'Retornos (%)',
            'oc_percentage': 'Ocupación Centros (%)',
            'vd_percentage': 'Vigilancias Defensivas (%)',
            'ocas_atz': 'Ocasiones Creadas',
            'ocas_rival': 'Ocasiones Recibidas',
            'dif_ocas': 'Diferencia Ocasiones'
        }
        
        metric_name = metric_names.get(metric, metric)
        
        # Preparar etiquetas para los partidos
        df['match_label'] = df.apply(lambda row: f"{row['match']} - {row['descripcion']}", axis=1)
        
        # 1. Gráfico de evolución
        evolution_fig = px.line(
            df, 
            x='fecha_parsed', 
            y=metric,
            markers=True,
            labels={
                'fecha_parsed': 'Fecha',
                metric: metric_name
            },
            title=f'Evolución de {metric_name} a lo largo de la temporada'
        )
        
        evolution_fig.update_traces(line=dict(width=3), marker=dict(size=10))
        evolution_fig.update_layout(
            xaxis_title="Fecha",
            yaxis_title=metric_name,
            hovermode="closest",
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=40, r=20, t=40, b=40)
        )
        
        # Añadir etiquetas de los partidos al gráfico de evolución
        evolution_fig.update_traces(
            hovertemplate='<b>%{text}</b><br>Fecha: %{x|%d/%m/%Y}<br>' + metric_name + ': %{y:.2f}',
            text=df['match_label']
        )
        
        # 2. Gráfico comparativo Liga vs Copa
        # Crear un DataFrame agrupado por tipo de partido
        df_comp = df.groupby('match_type')[metric].mean().reset_index()
        
        comparative_fig = px.bar(
            df_comp,
            x='match_type',
            y=metric,
            color='match_type',
            text=df_comp[metric].apply(lambda x: f'{x:.2f}'),
            labels={
                'match_type': 'Tipo de Partido',
                metric: metric_name
            },
            title=f'Comparativa de {metric_name} por tipo de partido',
            color_discrete_map={'Liga': '#3498db', 'Copa': '#e74c3c'}
        )
        
        comparative_fig.update_layout(
            xaxis_title="Tipo de Partido",
            yaxis_title=metric_name,
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=40, r=20, t=40, b=40)
        )
        
        # 3. Gráfico de distribución por rango
        # Definir rangos según el tipo de métrica
        if metric in ['ocas_atz', 'ocas_rival', 'dif_ocas']:
            # Para ocasiones, usar rangos enteros
            bins = [-10, -5, 0, 5, 10, 15, 20]
            labels = ['<-5', '-5 a 0', '0 a 5', '5 a 10', '10 a 15', '>15']
        else:
            # Para porcentajes, usar rangos de porcentaje
            bins = [0, 30, 50, 70, 90, 100]
            labels = ['0-30%', '30-50%', '50-70%', '70-90%', '90-100%']
        
        df['range'] = pd.cut(df[metric], bins=bins, labels=labels, include_lowest=True)
        df_dist = df['range'].value_counts().reset_index()
        df_dist.columns = ['range', 'count']
        
        distribution_fig = px.pie(
            df_dist,
            values='count',
            names='range',
            title=f'Distribución de {metric_name} por rango',
            hole=0.4
        )
        
        distribution_fig.update_layout(
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family="Arial, sans-serif", size=12),
            margin=dict(l=20, r=20, t=40, b=20)
        )
        
        # Calcular estadísticas para las tarjetas
        avg_value = df[metric].mean()
        best_row = df.loc[df[metric].idxmax()]
        worst_row = df.loc[df[metric].idxmin()]
        
        # Para las métricas de porcentaje, añadir el símbolo %
        is_percentage = 'percentage' in metric
        
        # Formatear valores según el tipo de métrica
        if is_percentage:
            avg_display = f"{avg_value:.2f}%"
            best_display = f"{best_row[metric]:.2f}%"
            worst_display = f"{worst_row[metric]:.2f}%"
        else:
            avg_display = f"{avg_value:.1f}"
            best_display = f"{best_row[metric]:.1f}"
            worst_display = f"{worst_row[metric]:.1f}"
        
        # Etiquetas para los mejores/peores partidos
        best_match = f"{best_row['match']} - {best_row['descripcion']} ({best_row['fecha']})"
        worst_match = f"{worst_row['match']} - {worst_row['descripcion']} ({worst_row['fecha']})"
        
        # Calcular la tendencia
        # Usar los últimos 3 partidos vs promedio general
        if len(df) >= 3:
            last_3 = df.tail(3)[metric].mean()
            if last_3 > avg_value * 1.05:  # 5% mejor que el promedio
                trend = html.Div([
                    html.I(className="fa fa-arrow-up text-success", style={"fontSize": "24px"}),
                    html.Span(" Mejorando", className="text-success ms-2")
                ])
            elif last_3 < avg_value * 0.95:  # 5% peor que el promedio
                trend = html.Div([
                    html.I(className="fa fa-arrow-down text-danger", style={"fontSize": "24px"}),
                    html.Span(" Empeorando", className="text-danger ms-2")
                ])
            else:
                trend = html.Div([
                    html.I(className="fa fa-arrows-h text-warning", style={"fontSize": "24px"}),
                    html.Span(" Estable", className="text-warning ms-2")
                ])
        else:
            trend = "Insuficientes datos"
        
        return evolution_fig, comparative_fig, distribution_fig, avg_display, best_display, worst_display, best_match, worst_match, trend