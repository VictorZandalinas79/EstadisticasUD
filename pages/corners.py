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
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # Seleccionar solo las columnas necesarias
        query = """
        SELECT ID as id, idcode, player, team, idgroup, idtext, secundary, 
               descripcion, mins as minute, xStart, yStart, xEnd, yEnd
        FROM bot_events 
        WHERE idcode = 'Corner' AND team = 'UD Atzeneta'
        """
        
        # Construir condiciones de filtro más eficientes
        params = []
        
        if players and len(players) > 0 and 'all' not in players:
            placeholders = ', '.join(['%s'] * len(players))
            query += f" AND player IN ({placeholders})"
            params.extend(players)
            
        if descriptions and len(descriptions) > 0 and 'all' not in descriptions:
            placeholders = ', '.join(['%s'] * len(descriptions))
            query += f" AND descripcion IN ({placeholders})"
            params.extend(descriptions)
        
        # Añadir un límite para evitar cargar demasiados datos
        query += " LIMIT 500"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return pd.DataFrame(results)
        
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
        corner_info['secundary'] = first_record.get('secundary', None)  # Rematador
        
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
            elif record['idgroup'] == 'Zona remate':
                corner_info['zona_remate'] = record['idtext']
                # Guardar coordenadas de remate si existen
                if 'xPort' in record and 'yPort' in record:
                    corner_info['xRemate'] = record['xPort']
                    corner_info['yRemate'] = record['yPort']
        
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
    
    # 2. Gráfica de barras de rematadores
    rematadores_fig = None
    if 'secundary' in df_corner_analysis.columns:
        # Eliminar valores nulos en secundary
        df_rematadores = df_corner_analysis.dropna(subset=['secundary'])
        
        if not df_rematadores.empty:
            # Contar ocurrencias de cada rematador
            rematadores_counts = df_rematadores['secundary'].value_counts().reset_index()
            rematadores_counts.columns = ['Rematador', 'Cantidad']
            
            # Ordenar por cantidad descendente y tomar los 10 principales
            rematadores_counts = rematadores_counts.sort_values('Cantidad', ascending=False).head(10)
            
            # Crear gráfica de barras
            rematadores_fig = px.bar(
                rematadores_counts,
                x='Rematador',
                y='Cantidad',
                title='Principales Rematadores',
                color='Cantidad',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            
            # Mejorar la apariencia
            rematadores_fig.update_layout(
                xaxis_title="Rematador",
                yaxis_title="Número de remates",
                plot_bgcolor='rgba(0,0,0,0.02)',
                xaxis={'categoryorder':'total descending'}
            )
    
    # 3. Análisis por zona de remate
    zona_remate_fig = None
    if 'zona_remate' in df_corner_analysis.columns:
        zonas_remate = df_corner_analysis.dropna(subset=['zona_remate'])
        
        if not zonas_remate.empty:
            # Contar ocurrencias por zona de remate y nivel de peligrosidad
            if 'chance' in zonas_remate.columns:
                zona_chance_counts = zonas_remate.groupby(['zona_remate', 'chance']).size().reset_index(name='count')
                
                # Crear gráfica de barras agrupadas
                zona_remate_fig = px.bar(
                    zona_chance_counts,
                    x='zona_remate',
                    y='count',
                    color='chance',
                    title='Zonas de Remate por Nivel de Peligrosidad',
                    barmode='group',
                    color_discrete_map={
                        'Alta': 'red',
                        'Media': 'orange',
                        'Leve': 'yellow',
                        'Sin ocasión': 'gray'
                    }
                )
                
                # Mejorar la apariencia
                zona_remate_fig.update_layout(
                    xaxis_title="Zona de Remate",
                    yaxis_title="Número de Remates",
                    legend_title="Peligrosidad",
                    plot_bgcolor='rgba(0,0,0,0.02)'
                )
    
    # Crear componente con las visualizaciones
    viz_components = []
    
    # Añadir título
    viz_components.append(html.H4(title, className="mb-4"))
    
    # Añadir gráfico de pizza y campograma lado a lado
    row_children = []
    
    # Columna para el gráfico de pizza
    if chance_fig:
        row_children.append(dbc.Col(
            dcc.Graph(figure=chance_fig, style={"height": "500px"}),  # Aumenta la altura
            md=5, className="px-1"  # Reduce el padding horizontal
        ))
    
    # Columna para el campograma
    row_children.append(dbc.Col(
        create_corner_pitch_visualization(df_corner_analysis),
        md=7, className="px-1"  # Reduce el padding horizontal
    ))
    
    viz_components.append(dbc.Row(row_children, className="mb-2"))
    
    # Nueva fila para gráficas adicionales
    row2_children = []
    
    # Gráfica de barras de rematadores
    if rematadores_fig:
        row2_children.append(dbc.Col(
            dcc.Graph(figure=rematadores_fig, style={"height": "400px"}),
            md=5, className="px-1"
        ))
    
    # Campograma con zonas de remate
    row2_children.append(dbc.Col(
        create_remate_pitch_visualization(df_corner_analysis),
        md=7, className="px-1"
    ))
    
    if row2_children:
        viz_components.append(html.H4("Análisis de Rematadores", className="mt-4 mb-3"))
        viz_components.append(dbc.Row(row2_children, className="mb-2"))
    
    # Tercera fila para zonas de remate (si es necesario)
    if zona_remate_fig:
        viz_components.append(dbc.Row([
            dbc.Col(
                dcc.Graph(figure=zona_remate_fig, style={"height": "400px"}),
                width=12, className="px-1"
            )
        ], className="mb-3"))
    
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

# Función campograma para rematadores
def create_remate_pitch_visualization(df_corners):
    """
    Crea una visualización del campograma con las zonas de remate resaltadas
    
    Args:
        df_corners (DataFrame): Datos de córners con zonas de remate
    
    Returns:
        dcc.Graph: Gráfico interactivo con las zonas de remate
    """
    
    if df_corners.empty:
        return html.Div("No hay datos disponibles para visualizar en el campograma", 
                       className="text-center text-muted my-3")
    
    # Verificar si hay coordenadas de remate (usamos xEnd y yEnd en lugar de xRemate y yRemate)
    has_remate_coords = ('xEnd' in df_corners.columns and 'yEnd' in df_corners.columns)
    
    if not has_remate_coords:
        return html.Div("No se encontraron coordenadas de remate (xEnd/yEnd) para visualizar", 
                       className="text-center text-muted my-3")
    
    # Función para normalizar coordenadas (se mantiene igual)
    def normalize_coordinates(x, y):
        try:
            x = float(x)
            y = float(y)
        except (ValueError, TypeError):
            return None, None
        
        x_orig_min, x_orig_max = 4.0, 316.0
        y_orig_min, y_orig_max = 8.0, 478.0
        
        x_norm = ((x - x_orig_min) / (x_orig_max - x_orig_min)) * 100.0
        y_norm = 100.0 - ((y - y_orig_min) / (y_orig_max - y_orig_min)) * 100.0
        
        x_rotated = y_norm
        y_rotated = x_norm
        
        return x_rotated, y_rotated
    
    # Convertir las columnas numéricas (ahora usamos xEnd y yEnd)
    numeric_columns = ['xEnd', 'yEnd']
    for col in numeric_columns:
        if col in df_corners.columns:
            df_corners[col] = df_corners[col].astype(float)
    
    # Filtrar registros con coordenadas de remate válidas (usando xEnd y yEnd)
    df_remates = df_corners.dropna(subset=['xEnd', 'yEnd'])
    
    # Normalizar coordenadas para todos los remates
    normalized_remates = []
    
    for _, remate in df_remates.iterrows():
        if pd.notna(remate['xEnd']) and pd.notna(remate['yEnd']):
            x_remate, y_remate = normalize_coordinates(remate['xEnd'], remate['yEnd'])
            
            if x_remate is None or y_remate is None:
                continue
            
            # Determinar color basado en la peligrosidad
            if 'chance' in remate:
                if remate['chance'] == 'Alta':
                    color = 'red'
                elif remate['chance'] == 'Media':
                    color = 'orange'
                elif remate['chance'] == 'Leve':
                    color = 'yellow'
                elif remate['chance'] == 'Sin ocasión':
                    color = 'white'
                else:
                    color = 'blue'
            else:
                color = 'blue'
            
            # Crear objeto con información del remate
            remate_info = {
                'id': remate.get('id', None),
                'x_remate': y_remate,
                'y_remate': x_remate,
                'secundary': remate.get('secundary', 'Desconocido'),
                'color': color,
                'chance': remate.get('chance', 'Desconocida'),
                'zona_remate': remate.get('zona_remate', 'Desconocida')
            }
            
            normalized_remates.append(remate_info)
    
    if not normalized_remates:
        return html.Div("No se encontraron coordenadas válidas de remate", 
                       className="text-center text-muted my-3")
    
    try:
        # PASO 1: Crear la imagen del campo
        pitch = VerticalPitch(pitch_type='wyscout', 
                              half=True,
                              goal_type='box',
                              pitch_color='grass', 
                              line_color='white')
        
        fig, ax = plt.subplots(figsize=(9, 12))
        pitch.draw(ax=ax)
        
        # Dibujar zonas de remate como círculos sombreados
        for remate in normalized_remates:
            # Círculo sombreado para la zona de remate
            circle = plt.Circle(
                (remate['x_remate'], remate['y_remate']), 
                radius=3,  # Ajustar radio según necesidad
                color=remate['color'], 
                alpha=0.5,  # Semi-transparente
                zorder=2
            )
            ax.add_patch(circle)
        
        # Añadir título
        plt.title('Zonas de Remate', fontsize=15)
        
        # Añadir leyenda
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch
        
        legend_elements = [
            Patch(facecolor='red', alpha=0.5, label='Ocasión clarísima'),
            Patch(facecolor='orange', alpha=0.5, label='Ocasión clara'),
            Patch(facecolor='yellow', alpha=0.5, label='Remate sin importancia'),
            Patch(facecolor='white', alpha=0.5, label='Sin ocasión')
        ]
        ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.05),
                  frameon=False, ncol=4)
        
        # Ajustar los márgenes
        plt.tight_layout()
        
        # Convertir la figura a una imagen
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        # Obtener dimensiones de la imagen para establecer la relación de aspecto correcta
        from PIL import Image
        with Image.open(buf) as img:
            width, height = img.size
        buf.seek(0)
        
        # Codificar la imagen en base64
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        
        # PASO 2: Crear una nueva figura de Plotly que contendrá la imagen y las trazas interactivas
        plotly_fig = go.Figure()
        
        # Añadir la imagen como fondo
        plotly_fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{img_data}',
                xref="paper",
                yref="paper",
                x=0,
                y=1,
                sizex=1,
                sizey=1,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )
        
        # PASO 3: Función para invertir coordenadas X (donde 0 es 100 y 100 es 0)
        def invert_x(x):
            return 100 - x
        
        # PASO 4: Añadir trazas interactivas invisibles sobre la imagen
        for i, remate in enumerate(normalized_remates):
            hover_text = f"<b>Rematador:</b> {remate['secundary']}<br>" + \
                         f"<b>Peligrosidad:</b> {remate['chance']}"
            
            if 'zona_remate' in remate:
                hover_text += f"<br><b>Zona:</b> {remate['zona_remate']}"
            
            # Punto para la zona de remate (invisible pero detecta hover)
            plotly_fig.add_trace(go.Scatter(
                x=[invert_x(remate['x_remate'])],
                y=[remate['y_remate']],
                mode='markers',
                marker=dict(size=20, color=remate['color']),
                opacity=0,
                hoverinfo='text',
                hovertext=hover_text,
                showlegend=False
            ))
        
        # PASO 5: Configurar el layout para que se ajuste a la imagen
        aspect_ratio = height / width
        
        plotly_fig.update_layout(
            autosize=True,
            height=500,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                visible=False,
                range=[0, 100],
                fixedrange=True
            ),
            yaxis=dict(
                visible=False,
                range=[0, 100],
                scaleanchor="x",
                scaleratio=aspect_ratio,
                fixedrange=True
            ),
            showlegend=False,
            hovermode='closest'
        )
        
        # Devolver el gráfico interactivo
        return dcc.Graph(
            figure=plotly_fig,
            config={'displayModeBar': False},  # Ocultar la barra de herramientas de Plotly
            style={'width': '100%', 'height': '100%'}
        )
        
    except Exception as e:
        print(f"Error al crear el campograma de remates: {str(e)}")
        return html.Div(f"Error al crear el campograma de remates: {str(e)}", 
                       className="text-center text-danger my-3")

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
    Crea una visualización interactiva de los lanzamientos de córners en un campograma
    con flechas curvas según el tipo de golpeo
    
    Args:
        df_corners (DataFrame): Datos de córners con coordenadas
    
    Returns:
        dcc.Graph: Gráfico interactivo con el campograma de córners
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
        
        # Normalizar al rango 0-100
        x_norm = ((x - x_orig_min) / (x_orig_max - x_orig_min)) * 100.0
        
        # Invertir el eje Y ya que en el sistema original Y aumenta hacia abajo
        y_norm = 100.0 - ((y - y_orig_min) / (y_orig_max - y_orig_min)) * 100.0
        
        # Para rotar 90 grados a la izquierda: (x,y) -> (y,100-x)
        # Esta transformación gira el campo para que la portería de ataque quede arriba
        x_rotated = y_norm
        y_rotated = x_norm
        
        return x_rotated, y_rotated
    
    # Convertir las columnas numéricas de Decimal a float
    numeric_columns = ['xStart', 'yStart', 'xEnd', 'yEnd']
    for col in numeric_columns:
        if col in df_corners.columns:
            df_corners[col] = df_corners[col].astype(float)
    
    # Determinar qué córners tienen golpeo Abierto o Cerrado
    kick_types = {}
    for _, row in df_corners.iterrows():
        if 'id' in row and 'idgroup' in row and 'idtext' in row:
            if row['idgroup'] == 'Golpeo':
                kick_types[row['id']] = row['idtext']
    
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
                    color = 'white'
                else:
                    color = 'blue'
            else:
                color = 'blue'
            
            # Determinar tipo de curva para la flecha según el tipo de golpeo
            is_curved = False
            curve_type = None
            corner_id = corner.get('id')
            
            if corner_id in kick_types:
                if kick_types[corner_id] == 'Cerrado':
                    is_curved = True
                    curve_type = 'Cerrado'  # cóncavo
                elif kick_types[corner_id] == 'Abierto':
                    is_curved = True
                    curve_type = 'Abierto'  # convexo
            
            # Si no tenemos la información de idgroup/idtext, intentar obtenerla de kick_type
            if not is_curved and 'kick_type' in corner:
                if corner['kick_type'] == 'Cerrado':
                    is_curved = True
                    curve_type = 'Cerrado'
                elif corner['kick_type'] == 'Abierto':
                    is_curved = True
                    curve_type = 'Abierto'
            
            # Crear objeto con información completa del córner
            corner_info = {
                'id': corner.get('id', None),
                'x_start': x_start,
                'y_start': y_start,
                'x_end': x_end,
                'y_end': y_end,
                'player': corner.get('player', 'Desconocido'),
                'color': color,
                'chance': corner.get('chance', 'Desconocida'),
                'descripcion': corner.get('descripcion', 'Sin descripción'),
                'minute': corner.get('minute', 'Desconocido'),
                'is_curved': is_curved,
                'curve_type': curve_type
            }
            
            # Añadir campos adicionales si existen
            for field in ['side', 'kick_type', 'defense_type', 'landing']:
                if field in corner:
                    corner_info[field] = corner[field]
                    
            normalized_corners.append(corner_info)
    
    if not normalized_corners:
        return html.Div("No se encontraron coordenadas válidas para los lanzamientos de córner", 
                       className="text-center text-muted my-3")
    
    try:
        # PASO 1: Crear la imagen del campo exactamente como en el código original
        pitch = VerticalPitch(pitch_type='wyscout', 
                              half=True,
                              goal_type='box',
                              pitch_color='grass', 
                              line_color='white')
        
        fig, ax = plt.subplots(figsize=(9, 12))  # Usar el mismo tamaño que en el original
        pitch.draw(ax=ax)
        
        # Dibujar los córners para obtener la imagen base
        for corner in normalized_corners:
            if corner['is_curved']:
                # Calcular el punto medio entre inicio y fin
                mid_x = (corner['x_start'] + corner['x_end']) / 2
                mid_y = (corner['y_start'] + corner['y_end']) / 2
                
                # Calcular vector dirección (de inicio a fin)
                vx = corner['x_end'] - corner['x_start']
                vy = corner['y_end'] - corner['y_start']
                length = np.sqrt(vx**2 + vy**2)
                
                if length > 0:
                    # Vector perpendicular unitario - IMPORTANTE: invertir x por y
                    # Ya que ahora x es realmente el eje vertical y y el horizontal
                    nx = vx / length  # Usamos el vector directo (no perpendicular)
                    ny = -vy / length  # Negamos para obtener perpendicular correcto
                    
                    # Ajustar la dirección según el tipo de curva
                    curve_strength = length * 0.3  # Ajusta la curvatura
                    
                    # Invertimos la lógica para Cerrado/Abierto
                    if corner['curve_type'] == 'Abierto':  # Convexo
                        nx = -nx
                        ny = -ny
                    
                    # Calcular el punto de control
                    control_x = mid_x + nx * curve_strength
                    control_y = mid_y + ny * curve_strength
                    
                    # Crear la curva con múltiples puntos
                    t_values = np.linspace(0, 1, 50)
                    curve_x = []
                    curve_y = []
                    
                    for t in t_values:
                        # Fórmula para una curva cuadrática de Bézier
                        x = (1-t)**2 * corner['y_start'] + 2*(1-t)*t * control_y + t**2 * corner['y_end']
                        y = (1-t)**2 * corner['x_start'] + 2*(1-t)*t * control_x + t**2 * corner['x_end']
                        curve_x.append(x)
                        curve_y.append(y)
                    
                    # Dibujar la curva
                    ax.plot(curve_x, curve_y, color=corner['color'], alpha=0.7, linewidth=2)
                    
                    # Dibujar la flecha en el extremo
                    arrow_idx = len(curve_x) - 2  # Penúltimo punto
                    dx = curve_x[-1] - curve_x[arrow_idx]
                    dy = curve_y[-1] - curve_y[arrow_idx]
                    ax.arrow(curve_x[arrow_idx], curve_y[arrow_idx], dx, dy, 
                            head_width=2, head_length=2, fc=corner['color'], ec=corner['color'], alpha=0.7)
                else:
                    # Si la longitud es cero (puntos coincidentes), usar línea recta
                    pitch.lines(corner['x_start'], corner['y_start'],
                                corner['x_end'], corner['y_end'], 
                                comet=True, color=corner['color'], ax=ax, alpha=0.7)
            else:
                # Para líneas rectas, usar el método original
                pitch.lines(corner['x_start'], corner['y_start'],
                            corner['x_end'], corner['y_end'], 
                            comet=True, color=corner['color'], ax=ax, alpha=0.7)
            
            # Punto de origen del córner (siempre igual)
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
        
        # Convertir la figura a una imagen
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        # Obtener dimensiones de la imagen para establecer la relación de aspecto correcta
        from PIL import Image
        with Image.open(buf) as img:
            width, height = img.size
        buf.seek(0)
        
        # Codificar la imagen en base64
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        
        # PASO 2: Crear una nueva figura de Plotly que contendrá la imagen y las trazas interactivas
        plotly_fig = go.Figure()
        
        # Añadir la imagen como fondo
        plotly_fig.add_layout_image(
            dict(
                source=f'data:image/png;base64,{img_data}',
                xref="paper",
                yref="paper",
                x=0,
                y=1,
                sizex=1,
                sizey=1,
                sizing="stretch",
                opacity=1,
                layer="below"
            )
        )
        
        # PASO 3: Función para invertir coordenadas X (donde 0 es 100 y 100 es 0)
        def invert_x(x):
            return 100 - x
        
        # PASO 4: Añadir trazas interactivas invisibles sobre la imagen
        # Usamos opacity=0 para hacerlas invisibles pero detectables al pasar el cursor
        for i, corner in enumerate(normalized_corners):
            hover_text = f"<b>Jugador:</b> {corner['player']}<br>" + \
                         f"<b>Partido:</b> {corner['descripcion']}<br>" + \
                         f"<b>Minuto:</b> {corner['minute']}<br>" + \
                         f"<b>Peligrosidad:</b> {corner['chance']}"
            
            # Añadir información adicional si está disponible
            if 'kick_type' in corner:
                hover_text += f"<br><b>Tipo de golpeo:</b> {corner['kick_type']}"
            elif 'curve_type' in corner and corner['curve_type']:
                hover_text += f"<br><b>Tipo de golpeo:</b> {corner['curve_type']}"
            if 'side' in corner:
                hover_text += f"<br><b>Lado:</b> {corner['side']}"
            if 'defense_type' in corner:
                hover_text += f"<br><b>Tipo defensa:</b> {corner['defense_type']}"
            if 'landing' in corner:
                hover_text += f"<br><b>Caída:</b> {corner['landing']}"
            
            if corner['is_curved']:
                # Crear puntos para la curva en Plotly
                mid_x = (corner['x_start'] + corner['x_end']) / 2
                mid_y = (corner['y_start'] + corner['y_end']) / 2
                
                # Calcular vector dirección
                vx = corner['x_end'] - corner['x_start']
                vy = corner['y_end'] - corner['y_start']
                length = np.sqrt(vx**2 + vy**2)
                
                if length > 0:
                    # Vector perpendicular unitario - usando la misma lógica que arriba
                    nx = vx / length
                    ny = -vy / length
                    
                    # Ajustar la dirección según el tipo de curva
                    curve_strength = length * 0.3  # Ajusta la curvatura
                    
                    # Invertimos la lógica para Cerrado/Abierto
                    if corner['curve_type'] == 'Abierto':  # Convexo
                        nx = -nx
                        ny = -ny
                    
                    # Calcular el punto de control
                    control_x = mid_x + nx * curve_strength
                    control_y = mid_y + ny * curve_strength
                    
                    # Crear la curva con múltiples puntos
                    t_values = np.linspace(0, 1, 20)
                    curve_x = []
                    curve_y = []
                    
                    for t in t_values:
                        # Fórmula para una curva cuadrática de Bézier
                        x = (1-t)**2 * corner['x_start'] + 2*(1-t)*t * control_x + t**2 * corner['x_end']
                        y = (1-t)**2 * corner['y_start'] + 2*(1-t)*t * control_y + t**2 * corner['y_end']
                        curve_x.append(x)
                        curve_y.append(y)
                    
                    # Invertir coordenadas X para Plotly
                    curve_x = [invert_x(x) for x in curve_x]
                    
                    # Añadir la curva interactiva
                    plotly_fig.add_trace(go.Scatter(
                        x=curve_x,
                        y=curve_y,
                        mode='lines',
                        line=dict(color=corner['color'], width=10),
                        opacity=0,                                    # Invisible pero detecta hover
                        hoverinfo='text',
                        hovertext=hover_text,
                        showlegend=False
                    ))
                else:
                    # Si la longitud es cero, usar línea recta
                    plotly_fig.add_trace(go.Scatter(
                        x=[invert_x(corner['x_start']), invert_x(corner['x_end'])],
                        y=[corner['y_start'], corner['y_end']],
                        mode='lines',
                        line=dict(color=corner['color'], width=10),
                        opacity=0,
                        hoverinfo='text',
                        hovertext=hover_text,
                        showlegend=False
                    ))
            else:
                # Línea recta para el córner (invisible pero detecta hover) con eje X invertido
                plotly_fig.add_trace(go.Scatter(
                    x=[invert_x(corner['x_start']), invert_x(corner['x_end'])],
                    y=[corner['y_start'], corner['y_end']],
                    mode='lines',
                    line=dict(color=corner['color'], width=10),
                    opacity=0,
                    hoverinfo='text',
                    hovertext=hover_text,
                    showlegend=False
                ))
            
            # Punto para el origen (invisible pero detecta hover) con eje X invertido
            plotly_fig.add_trace(go.Scatter(
                x=[invert_x(corner['x_start'])],
                y=[corner['y_start']],
                mode='markers',
                marker=dict(size=10, color=corner['color']),
                opacity=0,
                hoverinfo='text',
                hovertext=hover_text,
                showlegend=False
            ))
        
        # PASO 5: Configurar el layout para que se ajuste a la imagen
        aspect_ratio = height / width
        
        plotly_fig.update_layout(
            autosize=True,
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                visible=False,
                range=[0, 100],
                fixedrange=True
            ),
            yaxis=dict(
                visible=False,
                range=[0, 100],
                scaleanchor="x",
                scaleratio=aspect_ratio,
                fixedrange=True
            ),
            showlegend=False,
            hovermode='closest'
        )
        
        # Devolver el gráfico interactivo
        return dcc.Graph(
            figure=plotly_fig,
            config={'displayModeBar': False},  # Ocultar la barra de herramientas de Plotly
            style={'width': '100%', 'height': '100%'}
        )
        
    except Exception as e:
        print(f"Error al crear el campograma: {str(e)}")
        return html.Div(f"Error al crear el campograma: {str(e)}", 
                       className="text-center text-danger my-3")

