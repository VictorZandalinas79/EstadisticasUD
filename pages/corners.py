"""
Corners - UD Atzeneta
Página de análisis de córners del equipo con filtros por jugador y descripción
"""
import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_login import login_required, current_user
import mysql.connector
from config import DB_CONFIG
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import io
import base64
from mplsoccer import VerticalPitch
from dash import html
import numpy as np

# Definición del layout de la página de córners
def corners_layout():
    return html.Div([
        dbc.Container([
            # Título de la página
            html.H2("Análisis de Córners", className="mb-4 mt-4"),
            
            # Imagen de equipo
            html.Div([
                html.Img(src="/assets/equipo.png", className="img-fluid rounded mb-4 w-100", 
                        style={"max-height": "300px", "object-fit": "cover"})
            ], className="text-center"),
            
            # Filtros para la visualización interactiva
            dbc.Card([
                dbc.CardHeader("Filtros de Análisis"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Lanzador:"),
                            dcc.Dropdown(
                                id="corner-player-selector",
                                placeholder="Selecciona un lanzador",
                                value=['all'],  # Valor por defecto "Todos"
                                className="mb-3",
                                multi=True
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Partido:"),
                            dcc.Dropdown(
                                id="corner-description-selector",
                                placeholder="Selecciona un partido",
                                value=['all'],  # Valor por defecto "Todos"
                                className="mb-3",
                                multi=True
                            )
                        ], md=6)
                    ])
                ])
            ], className="mb-4"),
            
            # Visualización interactiva principal
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Desempeño en Córners"),
                        dbc.CardBody([
                            dcc.Loading(
                                id="corner-vis-loading",
                                type="circle",
                                children=[
                                    html.Div(id="corner-visualization")
                                ]
                            )
                        ])
                    ])
                ], className="mb-4")
            ]),
            
            # Información detallada
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Detalles de Rendimiento"),
                        dbc.CardBody(id="corner-detailed-stats")
                    ])
                ], className="mb-4")
            ])
        ], fluid=True)
    ])

# Función para obtener datos de córners con filtros
def get_filtered_corners_data(players=None, descriptions=None):
    """
    Obtiene datos de córners de la base de datos MySQL con filtros
    
    Args:
        players (list): Lista de jugadores a filtrar
        descriptions (list): Lista de descripciones (partidos) a filtrar
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de córners filtrados
    """
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Construir la consulta SQL base - AÑADIR xStart, yStart, xEnd, yEnd a la consulta
        query = """
        SELECT ID as id, idcode, player, team, idgroup, idtext, descripcion, mins as minute,
               xStart, yStart, xEnd, yEnd
        FROM bot_events 
        WHERE idcode = 'Corner'
        """
        
        # Añadir condiciones de filtro si existen
        conditions = []
        params = []
        
        # Siempre filtrar por equipo UD Atzeneta
        conditions.append("team = 'UD Atzeneta'")
        
        if players and len(players) > 0 and 'all' not in players:
            placeholders = ', '.join(['%s'] * len(players))
            conditions.append(f"player IN ({placeholders})")
            params.extend(players)
            
        if descriptions and len(descriptions) > 0 and 'all' not in descriptions:
            placeholders = ', '.join(['%s'] * len(descriptions))
            conditions.append(f"descripcion IN ({placeholders})")
            params.extend(descriptions)
            
        if conditions:
            query += " AND " + " AND ".join(conditions)
        
        # Ejecutar la consulta
        cursor.execute(query, params)
        
        # Obtener todos los resultados
        results = cursor.fetchall()
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
        # Convertir a DataFrame de pandas
        df = pd.DataFrame(results)
        
        return df
        
    except Exception as e:
        print(f"Error al obtener datos de córners: {str(e)}")
        return pd.DataFrame()

# Función para cargar opciones de filtros
def load_filter_options():
    """
    Carga las opciones disponibles para los filtros de jugadores y descripciones/partidos
    
    Returns:
        tuple: (opciones_jugadores, opciones_descripciones)
    """
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Obtener jugadores únicos que han lanzado córners (solo UD Atzeneta)
        cursor.execute("""
            SELECT DISTINCT player 
            FROM bot_events 
            WHERE idcode = 'Corner' AND player IS NOT NULL AND player != '' AND team = 'UD Atzeneta'
            ORDER BY player
        """)
        players = [row['player'] for row in cursor.fetchall()]
        # Añadir opción "Todos" al principio
        player_options = [{'label': 'Todos', 'value': 'all'}] + [{'label': p, 'value': p} for p in players]
        
        # Obtener descripciones únicas (partidos)
        cursor.execute("""
            SELECT DISTINCT descripcion 
            FROM bot_events 
            WHERE idcode = 'Corner' AND descripcion IS NOT NULL AND descripcion != ''
            ORDER BY descripcion
        """)
        descriptions = [row['descripcion'] for row in cursor.fetchall()]
        # Añadir opción "Todos" al principio
        description_options = [{'label': 'Todos', 'value': 'all'}] + [{'label': d, 'value': d} for d in descriptions]
        
        # Cerrar la conexión
        cursor.close()
        conn.close()
        
        return player_options, description_options
        
    except Exception as e:
        print(f"Error al cargar opciones de filtro: {str(e)}")
        return [{'label': 'Todos', 'value': 'all'}], [{'label': 'Todos', 'value': 'all'}]

# Función para crear la visualización del córner
def create_corner_visualization(df_corners, selected_players, selected_descriptions):
    """
    Crea una visualización interactiva del desempeño en córners
    
    Args:
        df_corners (DataFrame): Datos filtrados de córners
        selected_players (list): Jugadores seleccionados
        selected_descriptions (list): Descripciones seleccionadas
        
    Returns:
        html.Div: Contenedor con la visualización
    """
    if df_corners.empty:
        return html.Div([
            html.H4("No hay datos disponibles con los filtros seleccionados", 
                   className="text-center text-muted my-5")
        ])
    
    # Título descriptivo
    title_parts = []
    if selected_players:
        title_parts.append(f"Jugadores: {', '.join(selected_players)}")
    if selected_descriptions:
        title_parts.append(f"Descripciones: {', '.join(selected_descriptions)}")
    
    title = "Análisis de córners"
    if title_parts:
        title += " - " + " | ".join(title_parts)
    
    # Agrupar córners por ID para análisis
    corner_ids = df_corners['id'].unique()
    
    # Preparar datos para la visualización
    corner_data = []
    
    for corner_id in corner_ids:
        corner_info = {}
        corner_records = df_corners[df_corners['id'] == corner_id]
        
        # Datos básicos
        first_record = corner_records.iloc[0]
        corner_info['id'] = corner_id
        corner_info['player'] = first_record['player']
        corner_info['descripcion'] = first_record['descripcion']
        corner_info['minute'] = first_record['minute']
        
        # Extraer atributos específicos
        for _, record in corner_records.iterrows():
            if record['idgroup'] == 'Lado':
                corner_info['side'] = record['idtext']
            elif record['idgroup'] == 'Golpeo':
                corner_info['kick_type'] = record['idtext']
            elif record['idgroup'] == 'Tipo defensa':
                corner_info['defense_type'] = record['idtext']
            elif record['idgroup'] == 'Caida lanzamiento':
                corner_info['landing'] = record['idtext']
            elif record['idgroup'] == 'Ocasión':
                corner_info['chance'] = record['idtext']
        
        corner_data.append(corner_info)
    
    # Convertir a DataFrame para análisis
    df_corner_analysis = pd.DataFrame(corner_data)
    
    # Crear visualizaciones
    
    # 1. Gráfico de distribución de córners por jugador
    if selected_players and len(selected_players) > 1:
        player_dist_fig = px.bar(
            df_corner_analysis['player'].value_counts().reset_index(),
            x='player',
            y='count',
            labels={'player': 'Jugador', 'count': 'Número de córners'},
            title='Distribución de córners por jugador'
        )
    else:
        player_dist_fig = None
    
    # 2. Gráfico de distribución por descripción
    if selected_descriptions and len(selected_descriptions) > 1:
        desc_dist_fig = px.bar(
            df_corner_analysis['descripcion'].value_counts().reset_index(),
            x='descripcion',
            y='count',
            labels={'descripcion': 'Descripción', 'count': 'Número de córners'},
            title='Distribución de córners por descripción'
        )
    else:
        desc_dist_fig = None
    
    # 3. Gráfico de efectividad (ocasiones generadas)
    if 'chance' in df_corner_analysis.columns:
        chance_counts = df_corner_analysis['chance'].value_counts().reset_index()
        chance_fig = px.pie(
            chance_counts,
            values='count',
            names='chance',
            title='Ocasiones generadas',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        chance_fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        chance_fig = None
    
    # Crear componente con las visualizaciones
    viz_components = []
    
    # Añadir título
    viz_components.append(html.H4(title, className="mb-4"))
    
    # Añadir gráficos de distribución si hay múltiples selecciones
    if player_dist_fig or desc_dist_fig:
        row_children = []
        
        if player_dist_fig:
            row_children.append(dbc.Col(dcc.Graph(figure=player_dist_fig), md=6))
        
        if desc_dist_fig:
            row_children.append(dbc.Col(dcc.Graph(figure=desc_dist_fig), md=6))
        
        viz_components.append(dbc.Row(row_children, className="mb-4"))
    
    # Añadir gráfico de efectividad
    if chance_fig:
        viz_components.append(dbc.Row([
            dbc.Col(dcc.Graph(figure=chance_fig))
        ], className="mb-4"))
    
    # Añadir tabla resumen si hay pocos datos
    if len(df_corner_analysis) <= 20:
        viz_components.append(create_corners_table(df_corner_analysis))
    
    return html.Div(viz_components)

# Función para crear tabla de córners
def create_corners_table(df):
    """
    Crea una tabla con los córners analizados
    """
    # Seleccionar columnas relevantes
    table_cols = ['player', 'descripcion', 'minute', 'side', 'kick_type', 'chance']
    available_cols = [col for col in table_cols if col in df.columns]
    
    # Crear tabla
    table_header = [html.Thead(html.Tr([html.Th(col) for col in available_cols]))]
    
    table_body = [html.Tbody([
        html.Tr([html.Td(row[col]) for col in available_cols])
        for _, row in df.iterrows()
    ])]
    
    return dbc.Table(table_header + table_body, striped=True, bordered=True, hover=True)

# Función para crear el detalle de estadísticas
def create_detailed_stats(df_corners):
    """
    Crea una sección con estadísticas detalladas de los córners
    
    Args:
        df_corners (DataFrame): Datos filtrados de córners
        
    Returns:
        html.Div: Contenedor con estadísticas detalladas
    """
    if df_corners.empty:
        return html.P("No hay datos disponibles con los filtros seleccionados", 
                    className="text-center text-muted")
    
    # Agrupar córners por ID para análisis
    corner_ids = df_corners['id'].unique()
    corner_data = []
    
    for corner_id in corner_ids:
        corner_info = {}
        corner_records = df_corners[df_corners['id'] == corner_id]
        
        # Datos básicos
        first_record = corner_records.iloc[0]
        corner_info['player'] = first_record['player']
        corner_info['descripcion'] = first_record['descripcion']
        
        # Extraer atributos específicos
        for _, record in corner_records.iterrows():
            if record['idgroup'] == 'Lado':
                corner_info['side'] = record['idtext']
            elif record['idgroup'] == 'Golpeo':
                corner_info['kick_type'] = record['idtext']
            elif record['idgroup'] == 'Tipo defensa':
                corner_info['defense_type'] = record['idtext']
            elif record['idgroup'] == 'Caida lanzamiento':
                corner_info['landing'] = record['idtext']
            elif record['idgroup'] == 'Ocasión':
                # Mapear valores de idtext a categorías de chance
                occasion_text = record['idtext']
                if occasion_text == 'Ocasión clarisima':
                    corner_info['chance'] = 'Alta'
                elif occasion_text == 'Ocasión Clara':
                    corner_info['chance'] = 'Media'
                elif occasion_text == 'Remate sin importancia':
                    corner_info['chance'] = 'Leve'
                elif occasion_text == 'Sin ocasión':
                    corner_info['chance'] = 'Sin ocasión'
                else:
                    corner_info['chance'] = occasion_text  # Mantener el valor original si no coincide
        
        corner_data.append(corner_info)
    
    df_analysis = pd.DataFrame(corner_data)
    
    # Crear estadísticas
    stats_components = []
    
    # 1. Estadísticas generales
    stats_components.append(html.H4("Estadísticas Generales", className="mt-4"))
    
    general_stats = [
        ("Total de córners", len(df_analysis)),
        ("Jugadores distintos", df_analysis['player'].nunique()),
        ("Descripciones distintas", df_analysis['descripcion'].nunique())
    ]
    
    if 'chance' in df_analysis.columns:
        high_chance = len(df_analysis[df_analysis['chance'] == 'Alta'])
        med_chance = len(df_analysis[df_analysis['chance'] == 'Media'])
        low_chance = len(df_analysis[df_analysis['chance'] == 'Leve'])
        no_chance = len(df_analysis[df_analysis['chance'] == 'Sin ocasión'])
        
        general_stats.extend([
            ("Ocasiones clarísimas", high_chance),
            ("Ocasiones claras", med_chance),
            ("Remates sin importancia", low_chance),
            ("Sin ocasión", no_chance),
            ("Porcentaje de efectividad", f"{(high_chance + med_chance) / len(df_analysis) * 100:.1f}%")
        ])
    
    stats_components.append(html.Ul([
        html.Li(f"{stat[0]}: {stat[1]}") for stat in general_stats
    ], className="list-group mb-4"))
    
    # 2. Estadísticas por jugador (si hay más de uno)
    if 'player' in df_analysis.columns and df_analysis['player'].nunique() > 1:
        stats_components.append(html.H4("Por Jugador", className="mt-4"))
        
        player_stats = df_analysis.groupby('player').agg(
            total_corners=('player', 'size'),
            high_chance=('chance', lambda x: sum(x == 'Alta')),
            med_chance=('chance', lambda x: sum(x == 'Media')),
            low_chance=('chance', lambda x: sum(x == 'Leve')),
            no_chance=('chance', lambda x: sum(x == 'Sin ocasión'))
        ).reset_index()
        
        player_stats['effectiveness'] = (player_stats['high_chance'] + player_stats['med_chance']) / player_stats['total_corners'] * 100
        
        # Renombrar columnas para la tabla
        player_stats = player_stats.rename(columns={
            'player': 'Jugador',
            'total_corners': 'Total Córners',
            'high_chance': 'Ocasiones Clarísimas',
            'med_chance': 'Ocasiones Claras',
            'low_chance': 'Remates sin importancia',
            'no_chance': 'Sin ocasión',
            'effectiveness': 'Efectividad (%)'
        })
        
        stats_components.append(create_stats_table(player_stats))
    
    # 3. Estadísticas por descripción (si hay más de una)
    if 'descripcion' in df_analysis.columns and df_analysis['descripcion'].nunique() > 1:
        stats_components.append(html.H4("Por Partido", className="mt-4"))
        
        desc_stats = df_analysis.groupby('descripcion').agg(
            total_corners=('descripcion', 'size'),
            high_chance=('chance', lambda x: sum(x == 'Alta')),
            med_chance=('chance', lambda x: sum(x == 'Media')),
            low_chance=('chance', lambda x: sum(x == 'Leve')),
            no_chance=('chance', lambda x: sum(x == 'Sin ocasión'))
        ).reset_index()
        
        desc_stats['effectiveness'] = (desc_stats['high_chance'] + desc_stats['med_chance']) / desc_stats['total_corners'] * 100
        
        # Renombrar columnas para la tabla
        desc_stats = desc_stats.rename(columns={
            'descripcion': 'Partido',
            'total_corners': 'Total Córners',
            'high_chance': 'Ocasiones Clarísimas',
            'med_chance': 'Ocasiones Claras',
            'low_chance': 'Remates sin importancia',
            'no_chance': 'Sin ocasión',
            'effectiveness': 'Efectividad (%)'
        })
        
        stats_components.append(create_stats_table(desc_stats))
    
    return html.Div(stats_components)

# Función auxiliar para crear tablas de estadísticas
def create_stats_table(df):
    """
    Crea una tabla HTML a partir de un DataFrame
    """
    if df.empty:
        return html.P("No hay datos disponibles")
    
    return dbc.Table.from_dataframe(
        df.round(1),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )

# Registrar callbacks para la interactividad
def register_corners_callbacks(app):
    # Callback para cargar las opciones de filtro
    @app.callback(
        [Output("corner-player-selector", "options"),
         Output("corner-description-selector", "options")],
        [Input("corner-player-selector", "search_value"),
         Input("corner-description-selector", "search_value")]
    )
    @login_required
    def update_filter_options(search_player, search_description):
        player_options, description_options = load_filter_options()
        return player_options, description_options
    
    # Callback para actualizar la visualización al cambiar los filtros (sin botón)
    @app.callback(
        [Output("corner-visualization", "children"),
         Output("corner-detailed-stats", "children")],
        [Input("corner-player-selector", "value"),
         Input("corner-description-selector", "value")]
    )
    @login_required
    def update_corner_visualization(selected_players, selected_descriptions):
        # Valores predeterminados si no hay selecciones
        if not selected_players:
            selected_players = ['all']
        if not selected_descriptions:
            selected_descriptions = ['all']
            
        try:
            # Obtener datos filtrados
            df_corners = get_filtered_corners_data(
                players=selected_players,
                descriptions=selected_descriptions
            )
            
            if df_corners.empty:
                return (
                    html.Div([
                        html.H4("No hay datos con los filtros seleccionados", 
                               className="text-center text-muted my-5")
                    ]),
                    html.P("Prueba con otros filtros", className="text-center text-muted")
                )
            
            # Crear visualización
            visualization = create_corner_visualization(
                df_corners,
                selected_players if 'all' not in selected_players else [],
                selected_descriptions if 'all' not in selected_descriptions else []
            )
            
            # Crear estadísticas detalladas
            detailed_stats = create_detailed_stats(df_corners)
            
            return visualization, detailed_stats
            
        except Exception as e:
            print(f"Error al crear visualización: {str(e)}")
            return (
                html.Div([
                    html.H4(f"Error: {str(e)}", className="text-center text-danger my-5")
                ]),
                html.P(f"Error: {str(e)}", className="text-center text-danger")
            )
        
def create_corner_pitch_visualization(df_corners):
    """
    Crea una visualización de los lanzamientos de córners en un campograma usando mplsoccer
    
    Args:
        df_corners (DataFrame): Datos de córners con coordenadas
    
    Returns:
        html.Img: Imagen del campograma de córners
    """
    
    if df_corners.empty:
        return html.Div("No hay datos disponibles para visualizar en el campograma", 
                        className="text-center text-muted my-3")
    
    # Verificar si hay coordenadas
    has_coords = ('xStart' in df_corners.columns and 'yStart' in df_corners.columns and 
                 'xEnd' in df_corners.columns and 'yEnd' in df_corners.columns)
    
    if not has_coords:
        return html.Div("No se encontraron coordenadas para los lanzamientos de córner", 
                       className="text-center text-muted my-3")
    
    # Función para normalizar coordenadas del sistema original al sistema Wyscout
    def normalize_coordinates(x, y):
        # Convertir a float para evitar problemas con Decimal
        try:
            x = float(x)
            y = float(y)
        except (ValueError, TypeError):
            return None, None
        
        # Coordenadas originales del campo
        x_orig_min, x_orig_max = 4.0, 316.0
        y_orig_min, y_orig_max = 8.0, 478.0
        
        # Coordenadas destino (Wyscout)
        x_wyscout_min, x_wyscout_max = 0.0, 100.0
        y_wyscout_min, y_wyscout_max = 0.0, 100.0  # Invertimos porque en Wyscout el eje Y crece hacia arriba
        
        # Normalizar X
        x_norm = ((x - x_orig_min) / (x_orig_max - x_orig_min)) * (x_wyscout_max - x_wyscout_min) + x_wyscout_min
        
        # Normalizar Y e invertir (en el sistema Wyscout, y=0 es abajo y y=100 es arriba)
        y_norm = 100.0 - ((y - y_orig_min) / (y_orig_max - y_orig_min)) * (y_wyscout_max - y_wyscout_min) + y_wyscout_min
        
        return x_norm, y_norm
    
    # Convertir las columnas numéricas de Decimal a float
    numeric_columns = ['xStart', 'yStart', 'xEnd', 'yEnd']
    for col in numeric_columns:
        if col in df_corners.columns:
            df_corners[col] = df_corners[col].astype(float)
    
    # Normalizar coordenadas para todos los córners
    normalized_corners = []
    
    for _, corner in df_corners.iterrows():
        if pd.notna(corner['xStart']) and pd.notna(corner['yStart']) and pd.notna(corner['xEnd']) and pd.notna(corner['yEnd']):
            x_start, y_start = normalize_coordinates(corner['xStart'], corner['yStart'])
            x_end, y_end = normalize_coordinates(corner['xEnd'], corner['yEnd'])
            
            # Verificar que la normalización fue exitosa
            if x_start is None or y_start is None or x_end is None or y_end is None:
                continue
            
            # Determinar color basado en la peligrosidad
            if 'chance' in corner:
                if corner['chance'] == 'Alta':
                    color = 'red'
                elif corner['chance'] == 'Media':
                    color = 'orange'
                elif corner['chance'] == 'Leve':
                    color = 'yellow'
                elif corner['chance'] == 'Sin ocasión':
                    color = 'gray'
                else:
                    color = 'blue'
            else:
                color = 'blue'
            
            normalized_corners.append({
                'x_start': x_start,
                'y_start': y_start,
                'x_end': x_end,
                'y_end': y_end,
                'player': corner.get('player', 'Desconocido'),
                'color': color
            })
    
    if not normalized_corners:
        return html.Div("No se encontraron coordenadas válidas para los lanzamientos de córner", 
                       className="text-center text-muted my-3")
    
    try:
        # Crear la figura con mplsoccer
        pitch = VerticalPitch(pitch_type='wyscout', half=False, goal_type='box')
        
        fig, ax = plt.subplots(figsize=(10, 7))
        pitch.draw(ax=ax)
        
        # Dibujar cada córner
        for corner in normalized_corners:
            # Dibujar la trayectoria del córner
            pitch.lines(corner['x_start'], corner['y_start'],
                        corner['x_end'], corner['y_end'], 
                        comet=True, color=corner['color'], ax=ax, alpha=0.7)
            
            # Punto de origen del córner
            pitch.scatter(corner['x_start'], corner['y_start'], s=100, 
                         color=corner['color'], alpha=0.8, ax=ax)
        
        # Añadir título
        plt.title('Lanzamientos de Córners', fontsize=15)
        
        # Añadir leyenda
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='red', lw=2, label='Ocasión clarísima'),
            Line2D([0], [0], color='orange', lw=2, label='Ocasión clara'),
            Line2D([0], [0], color='yellow', lw=2, label='Remate sin importancia'),
            Line2D([0], [0], color='gray', lw=2, label='Sin ocasión')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  frameon=False, ncol=4)
        
        # Ajustar los márgenes
        plt.tight_layout()
        
        # Convertir la figura a una imagen para Dash
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        # Codificar la imagen en base64
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        
        # Devolver la imagen como un componente HTML
        return html.Img(src=f'data:image/png;base64,{img_data}',
                       style={'width': '100%', 'height': 'auto'})
    
    except Exception as e:
        print(f"Error al crear el campograma: {str(e)}")
        return html.Div(f"Error al crear el campograma: {str(e)}", 
                       className="text-center text-danger my-3")

# Función para integrar el campograma en la visualización principal
def create_corner_visualization(df_corners, selected_players, selected_descriptions):
    """
    Crea una visualización interactiva del desempeño en córners
    
    Args:
        df_corners (DataFrame): Datos filtrados de córners
        selected_players (list): Jugadores seleccionados
        selected_descriptions (list): Descripciones seleccionadas
        
    Returns:
        html.Div: Contenedor con la visualización
    """
    if df_corners.empty:
        return html.Div([
            html.H4("No hay datos disponibles con los filtros seleccionados", 
                   className="text-center text-muted my-5")
        ])
    
    # Título descriptivo
    title_parts = []
    if selected_players:
        title_parts.append(f"Jugadores: {', '.join(selected_players)}")
    if selected_descriptions:
        title_parts.append(f"Descripciones: {', '.join(selected_descriptions)}")
    
    title = "Análisis de córners"
    if title_parts:
        title += " - " + " | ".join(title_parts)
    
    # Agrupar córners por ID para análisis
    corner_ids = df_corners['id'].unique()
    
    # Preparar datos para la visualización
    corner_data = []
    
    for corner_id in corner_ids:
        corner_info = {}
        corner_records = df_corners[df_corners['id'] == corner_id]
        
        # Datos básicos
        first_record = corner_records.iloc[0]
        corner_info['id'] = corner_id
        corner_info['player'] = first_record['player']
        corner_info['descripcion'] = first_record['descripcion']
        corner_info['minute'] = first_record['minute']
        
        # Extraer coordenadas si están disponibles
        if 'xStart' in first_record and 'yStart' in first_record:
            corner_info['xStart'] = first_record['xStart']
            corner_info['yStart'] = first_record['yStart']
        
        if 'xEnd' in first_record and 'yEnd' in first_record:
            corner_info['xEnd'] = first_record['xEnd']
            corner_info['yEnd'] = first_record['yEnd']
        
        # Extraer atributos específicos
        for _, record in corner_records.iterrows():
            if record['idgroup'] == 'Lado':
                corner_info['side'] = record['idtext']
            elif record['idgroup'] == 'Golpeo':
                corner_info['kick_type'] = record['idtext']
            elif record['idgroup'] == 'Tipo defensa':
                corner_info['defense_type'] = record['idtext']
            elif record['idgroup'] == 'Caida lanzamiento':
                corner_info['landing'] = record['idtext']
            elif record['idgroup'] == 'Ocasión':
                # Mapear valores de idtext a categorías de chance
                occasion_text = record['idtext']
                if occasion_text == 'Ocasión clarisima':
                    corner_info['chance'] = 'Alta'
                elif occasion_text == 'Ocasión Clara':
                    corner_info['chance'] = 'Media'
                elif occasion_text == 'Remate sin importancia':
                    corner_info['chance'] = 'Leve'
                elif occasion_text == 'Sin ocasión':
                    corner_info['chance'] = 'Sin ocasión'
                else:
                    corner_info['chance'] = occasion_text
        
        corner_data.append(corner_info)
    
    # Convertir a DataFrame para análisis
    df_corner_analysis = pd.DataFrame(corner_data)
    
    # Crear visualizaciones
    
    # 1. Gráfico de efectividad (ocasiones generadas)
    if 'chance' in df_corner_analysis.columns:
        chance_counts = df_corner_analysis['chance'].value_counts().reset_index()
        chance_fig = px.pie(
            chance_counts,
            values='count',
            names='chance',
            title='Ocasiones generadas',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        chance_fig.update_traces(textposition='inside', textinfo='percent+label')
    else:
        chance_fig = None
    
    # Crear componente con las visualizaciones
    viz_components = []
    
    # Añadir título
    viz_components.append(html.H4(title, className="mb-4"))
    
    # Añadir gráfico de pizza y campograma lado a lado
    row_children = []
    
    # Columna para el gráfico de pizza
    if chance_fig:
        row_children.append(dbc.Col(dcc.Graph(figure=chance_fig), md=6))
    
    # Columna para el campograma
    row_children.append(dbc.Col(create_corner_pitch_visualization(df_corner_analysis), md=6))
    
    viz_components.append(dbc.Row(row_children, className="mb-4"))
    
    # Añadir tabla resumen si hay pocos datos
    if len(df_corner_analysis) <= 20:
        viz_components.append(create_corners_table(df_corner_analysis))
    
    return html.Div(viz_components)