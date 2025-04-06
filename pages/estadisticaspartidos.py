"""
Estadísticas de Partidos - UD Atzeneta
Página de análisis de estadísticas de partidos del equipo con datos de Google Sheets
"""
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask_login import login_required, current_user
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# Función para obtener datos de Google Sheets
def get_sheet_data(sheet_name):
    """
    Obtiene datos de una hoja específica de Google Sheets.
    
    Args:
        sheet_name (str): Nombre de la hoja dentro del documento de Google Sheets
        
    Returns:
        pandas.DataFrame: DataFrame con los datos de la hoja
    """
    try:
        # Define el alcance y credenciales
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Ruta al archivo de credenciales
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'google_credentials.json')
        
        # Si no existe el directorio, crearlo
        credentials_dir = os.path.join(os.path.dirname(__file__), '..', 'credentials')
        if not os.path.exists(credentials_dir):
            os.makedirs(credentials_dir)
        
        # Verificar si existe el archivo de credenciales
        if not os.path.exists(credentials_path):
            print(f"Error: No se encontró el archivo de credenciales en: {credentials_path}")
            print("Por favor, crea el archivo de credenciales manualmente.")
            # Devolver DataFrame vacío si no hay credenciales
            return pd.DataFrame()
        
        # Cargar credenciales desde el archivo
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        
        # Autorizar el cliente
        client = gspread.authorize(credentials)
        
        # ID de tu hoja de cálculo de Google Sheets
        sheet_id = "1J_1zx47gVABl6zapYBNygpe3lmEnFjLcpH-MdGuTC28"
        
        # Abrir el documento por ID
        try:
            print(f"Intentando abrir documento con ID: {sheet_id}")
            spreadsheet = client.open_by_key(sheet_id)
            
            # Mostrar los nombres de todas las hojas disponibles (para depuración)
            sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]
            print(f"Hojas disponibles: {sheet_names}")
            
            # Seleccionar una hoja específica (la que quieres usar)
            print(f"Intentando acceder a la hoja: '{sheet_name}'")
            worksheet = spreadsheet.worksheet(sheet_name)
            
            # Obtener todos los valores y los encabezados por separado para manejar duplicados
            print(f"Obteniendo datos de la hoja: '{sheet_name}'")
            
            # Obtener los valores y los encabezados por separado
            all_values = worksheet.get_all_values()
            
            if not all_values:
                print(f"La hoja '{sheet_name}' no contiene datos.")
                return pd.DataFrame()
            
            # La primera fila son los encabezados
            headers = all_values[0]
            data_rows = all_values[1:]
            
            print(f"Encabezados originales: {headers}")
            
            # Detectar y corregir encabezados duplicados
            fixed_headers = []
            header_counts = {}
            
            for h in headers:
                if h in header_counts:
                    header_counts[h] += 1
                    fixed_headers.append(f"{h}_{header_counts[h]}")
                else:
                    header_counts[h] = 0
                    fixed_headers.append(h)
            
            if headers != fixed_headers:
                print(f"Se corrigieron encabezados duplicados: {fixed_headers}")
            
            # Crear DataFrame directamente con los valores y los encabezados corregidos
            df = pd.DataFrame(data_rows, columns=fixed_headers)
            
            # Convertir las columnas numéricas
            numeric_columns = ['Dorsal', 'Tiempo', 'GF', 'GC', 'Asist', 'TA', 'TR', 'Jornada']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            print(f"DataFrame creado con {len(df)} filas y {len(df.columns)} columnas")
            
            # Añadir timestamp para verificar cuándo se actualizaron los datos
            print(f"Datos actualizados de Google Sheets (hoja: {sheet_name}) a las {datetime.now().strftime('%H:%M:%S')}")
            
            return df
            
        except gspread.exceptions.SpreadsheetNotFound:
            print(f"No se encontró la hoja de cálculo con ID: {sheet_id}")
            return pd.DataFrame()
        
        except gspread.exceptions.WorksheetNotFound:
            print(f"No se encontró la hoja '{sheet_name}' en el documento")
            return pd.DataFrame()
    
    except Exception as e:
        print(f"Error al obtener datos de Google Sheets: {str(e)}")
        # En caso de error, devolver un DataFrame vacío
        return pd.DataFrame()

# Definición del layout de la página de estadísticas de partidos
def estadisticaspartidos_layout():
    """
    Función que devuelve el layout para la página de estadísticas de partidos
    """
    return html.Div([
        dbc.Container([
            # Título de la página
            html.H2("Análisis de Estadísticas de Jugadores", className="mb-4 mt-4"),
            
            # Selector de hoja - Añadido para seleccionar la hoja específica
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Seleccionar Hoja", className="mb-2"),
                        dcc.Dropdown(
                            id='sheet-dropdown',
                            options=[
                                # Reemplaza estos valores con los nombres reales de tus hojas
                                {'label': 'Jugadores Estadisticas', 'value': 'Jugadores Estadisticas'},
                                {'label': 'Registros Partido', 'value': 'Registros Partido'}
                            ],
                            value='Jugadores Estadisticas',  # Hoja por defecto
                            clearable=False,
                            className="mb-3"
                        ),
                    ], className="p-3 bg-light rounded mb-4")
                ], width=12)
            ]),
            
            # Filtros y controles
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Filtros", className="mb-2"),
                        html.Label("Jornada:"),
                        dcc.Dropdown(
                            id='jornada-dropdown',
                            options=[{'label': 'Todas', 'value': 'todas'}],  # Se actualizará dinámicamente
                            value='todas',
                            clearable=False,
                            className="mb-3"
                        ),
                        html.Label("Posición:"),
                        dcc.Dropdown(
                            id='posicion-dropdown',
                            options=[{'label': 'Todas', 'value': 'todas'}],  # Se actualizará dinámicamente
                            value='todas',
                            clearable=False,
                            className="mb-3"
                        ),
                        html.Label("Jugador:"),
                        dcc.Dropdown(
                            id='jugador-dropdown',
                            options=[{'label': 'Todos', 'value': 'todos'}],  # Se actualizará dinámicamente
                            value='todos',
                            clearable=False,
                            className="mb-3"
                        ),
                        dbc.Button(
                            "Actualizar Datos", 
                            id="actualizar-datos-btn", 
                            color="primary", 
                            className="mt-2"
                        ),
                        html.Div(id="actualizacion-info", className="text-muted mt-2 small")
                    ], className="p-3 bg-light rounded")
                ], md=3),
                
                dbc.Col([
                    html.Div([
                        html.H5("Estadísticas de Jugadores", className="mb-3"),
                        
                        # Spinner para mostrar carga
                        dbc.Spinner(
                            html.Div(id="tabla-estadisticas-container", className="mt-1"),
                            color="primary",
                            type="border"
                        ),
                    ], className="mb-4"),
                    
                    # Sección para gráficos
                    html.Div([
                        html.H5("Visualización", className="mt-4 mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Estadística a visualizar:"),
                                dcc.Dropdown(
                                    id='estadistica-visualizar-dropdown',
                                    options=[
                                        {'label': 'Tiempo Jugado', 'value': 'Tiempo'},
                                        {'label': 'Goles a Favor', 'value': 'GF'},
                                        {'label': 'Goles en Contra', 'value': 'GC'},
                                        {'label': 'Asistencias', 'value': 'Asist'},
                                        {'label': 'Tarjetas Amarillas', 'value': 'TA'},
                                        {'label': 'Tarjetas Rojas', 'value': 'TR'}
                                    ],
                                    value='Tiempo',
                                    clearable=False
                                ),
                            ], md=6),
                            dbc.Col([
                                html.Label("Tipo de gráfico:"),
                                dcc.Dropdown(
                                    id='tipo-grafico-dropdown',
                                    options=[
                                        {'label': 'Barras', 'value': 'barras'},
                                        {'label': 'Línea', 'value': 'linea'},
                                        {'label': 'Pastel', 'value': 'pastel'},
                                        {'label': 'Dispersión', 'value': 'dispersion'}
                                    ],
                                    value='barras',
                                    clearable=False
                                ),
                            ], md=6)
                        ], className="mb-3"),
                        
                        dbc.Spinner(
                            dcc.Graph(id="grafico-estadisticas", figure={}),
                            color="primary",
                            type="border"
                        )
                    ], className="p-3 bg-light rounded")
                ], md=9)
            ]),
            
            # Sección de resumen
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H5("Resumen de Estadísticas", className="mb-3 mt-4"),
                        html.Div(id="resumen-estadisticas", className="p-3")
                    ], className="p-3 bg-light rounded mt-4")
                ])
            ]),
            
            # Espacio para almacenar datos entre callbacks
            dcc.Store(id='stored-estadisticas-data'),
            
            # Intervalo para actualización periódica (cada 5 minutos = 300000 ms)
            dcc.Interval(
                id='interval-estadisticas',
                interval=300000,
                n_intervals=0
            )
        ], fluid=True)
    ])

# Registrar callbacks
def register_estadisticaspartidos_callbacks(app):
    """
    Función para registrar los callbacks específicos de esta página
    """
    
    # Callback para cargar datos inicial y periódicamente
    @app.callback(
        Output('stored-estadisticas-data', 'data'),
        [Input('interval-estadisticas', 'n_intervals'),
         Input('actualizar-datos-btn', 'n_clicks'),
         Input('sheet-dropdown', 'value')]  # Añadido para seleccionar la hoja
    )
    def cargar_datos_estadisticas(n_intervals, n_clicks, selected_sheet):
        """Carga datos de Google Sheets"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Si no se seleccionó ninguna hoja, usar una por defecto
        if not selected_sheet:
            selected_sheet = 'Jugadores Estadisticas'  # Reemplaza con el nombre real de tu hoja
            
        try:
            # Obtener datos de Google Sheets - usar el nombre de la hoja seleccionada
            df = get_sheet_data(selected_sheet)
            
            if df.empty:
                # Si no hay datos, mostrar mensaje de error
                return {
                    'data': [], 
                    'timestamp': timestamp,
                    'error': f'No se pudieron obtener datos de la hoja "{selected_sheet}". Por favor, verifica la conexión y el nombre de la hoja.'
                }
            
            # Convertir las columnas numéricas
            numeric_columns = ['Dorsal', 'Tiempo', 'GF', 'GC', 'Asist', 'TA', 'TR']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Convertir DataFrame a diccionario para almacenar en dcc.Store
            return {'data': df.to_dict('records'), 'timestamp': timestamp, 'error': None}
            
        except Exception as e:
            print(f"Error al cargar datos: {e}")
            # En caso de error, devolver mensaje específico
            return {
                'data': [], 
                'timestamp': timestamp,
                'error': f'Error al cargar datos de la hoja "{selected_sheet}": {str(e)}'
            }
    
    # Callback para actualizar las opciones de filtro basadas en los datos
    @app.callback(
        [Output('jornada-dropdown', 'options'),
         Output('posicion-dropdown', 'options'),
         Output('jugador-dropdown', 'options')],
        [Input('stored-estadisticas-data', 'data')]
    )
    def actualizar_opciones_filtro(stored_data):
        """Actualiza las opciones de filtro basadas en los datos cargados"""
        if not stored_data or stored_data.get('error') or not stored_data.get('data'):
            # Valores por defecto si no hay datos
            return (
                [{'label': 'Todas', 'value': 'todas'}],
                [{'label': 'Todas', 'value': 'todas'}],
                [{'label': 'Todos', 'value': 'todos'}]
            )
        
        try:
            df = pd.DataFrame(stored_data['data'])
            
            # Obtener valores únicos para cada filtro
            # Verificar que las columnas existen antes de obtener valores únicos
            jornadas = [{'label': 'Todas', 'value': 'todas'}]
            if 'Jornada' in df.columns:
                jornadas.extend([{'label': str(j), 'value': str(j)} for j in sorted(df['Jornada'].unique())])
            
            posiciones = [{'label': 'Todas', 'value': 'todas'}]
            if 'Posicion' in df.columns:
                posiciones.extend([{'label': p, 'value': p} for p in sorted(df['Posicion'].unique())])
            
            jugadores = [{'label': 'Todos', 'value': 'todos'}]
            if 'Jugador' in df.columns:
                if 'Dorsal' in df.columns:
                    jugadores.extend([{'label': f"{j} ({d})", 'value': j} for j, d in 
                                     zip(df['Jugador'].unique(), df.groupby('Jugador')['Dorsal'].first().values)])
                else:
                    jugadores.extend([{'label': j, 'value': j} for j in sorted(df['Jugador'].unique())])
            
            return jornadas, posiciones, jugadores
            
        except Exception as e:
            print(f"Error al actualizar opciones de filtro: {e}")
            return (
                [{'label': 'Todas', 'value': 'todas'}],
                [{'label': 'Todas', 'value': 'todas'}],
                [{'label': 'Todos', 'value': 'todos'}]
            )
    
    # Callback para actualizar la tabla
    @app.callback(
        [Output('tabla-estadisticas-container', 'children'),
         Output('actualizacion-info', 'children')],
        [Input('stored-estadisticas-data', 'data'),
         Input('jornada-dropdown', 'value'),
         Input('posicion-dropdown', 'value'),
         Input('jugador-dropdown', 'value')]
    )
    def actualizar_tabla_estadisticas(stored_data, jornada, posicion, jugador):
        """Actualiza la tabla de estadísticas con los datos almacenados y filtrados"""
        if not stored_data:
            return html.Div("No hay datos disponibles."), ""
        
        timestamp = stored_data['timestamp']
        
        # Verificar si hay un error
        if stored_data.get('error'):
            return html.Div([
                html.Div(stored_data['error'], className="alert alert-danger")
            ]), f"Última actualización intentada: {timestamp}"
        
        # Verificar si hay datos
        if not stored_data.get('data'):
            return html.Div([
                html.Div("No hay datos disponibles.", className="alert alert-warning")
            ]), f"Última actualización: {timestamp}"
        
        df = pd.DataFrame(stored_data['data'])
        
        # Aplicar filtros si las columnas existen
        if jornada != 'todas' and 'Jornada' in df.columns:
            df = df[df['Jornada'].astype(str) == jornada]
        
        if posicion != 'todas' and 'Posicion' in df.columns:
            df = df[df['Posicion'] == posicion]
        
        if jugador != 'todos' and 'Jugador' in df.columns:
            df = df[df['Jugador'] == jugador]
        
        if df.empty:
            return html.Div([
                html.Div("No hay datos disponibles para los filtros seleccionados.", className="alert alert-warning")
            ]), f"Última actualización: {timestamp}"
        
        # Crear tabla interactiva
        tabla = dash_table.DataTable(
            id='tabla-estadisticas',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={
                'overflowX': 'auto',
                'minWidth': '100%',
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#0053A0',  # Color azul de UD Atzeneta
                'color': 'white',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f5f5f5'
                },
                # Destacar titulares (si existe la columna)
                {
                    'if': {
                        'filter_query': '{Titular} eq "Si" || {Titular} eq "Sí" || {Titular} eq "SI" || {Titular} eq "SÍ" || {Titular} eq true || {Titular} eq 1',
                    },
                    'backgroundColor': '#e6f7ff'  # Azul claro para titulares
                } if 'Titular' in df.columns else {},
                # Destacar goleadores (si existe la columna)
                {
                    'if': {
                        'filter_query': '{GF} > 0',
                    },
                    'backgroundColor': '#e6ffe6'  # Verde claro para goleadores
                } if 'GF' in df.columns else {},
                # Destacar tarjetas (si existen las columnas)
                {
                    'if': {
                        'filter_query': '{TA} > 0 || {TR} > 0',
                    },
                    'backgroundColor': '#fff9e6'  # Amarillo claro para amonestados
                } if 'TA' in df.columns or 'TR' in df.columns else {},
            ],
            sort_action='native',
            filter_action='native',
            page_action='native',
            page_size=10,
            export_format='xlsx',
            export_headers='display',
        )
        
        # Información de última actualización
        info_actualizacion = f"Última actualización: {timestamp}"
        
        return tabla, info_actualizacion
    
    # Callback para actualizar el gráfico
    @app.callback(
        Output('grafico-estadisticas', 'figure'),
        [Input('stored-estadisticas-data', 'data'),
         Input('estadistica-visualizar-dropdown', 'value'),
         Input('tipo-grafico-dropdown', 'value'),
         Input('jornada-dropdown', 'value'),
         Input('posicion-dropdown', 'value'),
         Input('jugador-dropdown', 'value')]
    )
    def actualizar_grafico_estadisticas(stored_data, estadistica, tipo_grafico, jornada, posicion, jugador):
        """Actualiza el gráfico basado en la estadística seleccionada, tipo de gráfico y filtros"""
        # Verificar si hay datos válidos
        if (not stored_data or 
            stored_data.get('error') or 
            not stored_data.get('data') or 
            len(stored_data['data']) == 0):
            
            # Devolver figura vacía con mensaje apropiado
            mensaje = "No hay datos disponibles para visualizar"
            
            if stored_data and stored_data.get('error'):
                mensaje = stored_data['error']
            
            return go.Figure().update_layout(
                title=mensaje,
                xaxis=dict(title=""),
                yaxis=dict(title=""),
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref="paper",
                        yref="paper",
                        text=mensaje,
                        showarrow=False,
                        font=dict(size=14)
                    )
                ]
            )
        
        df = pd.DataFrame(stored_data['data'])
        
        # Verificar si la estadística seleccionada existe en los datos
        if estadistica not in df.columns:
            return go.Figure().update_layout(
                title=f"La estadística '{estadistica}' no está disponible en esta hoja",
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref="paper",
                        yref="paper",
                        text=f"La columna '{estadistica}' no existe en los datos seleccionados.",
                        showarrow=False,
                        font=dict(size=14)
                    )
                ]
            )
        
        # Aplicar filtros si las columnas existen
        if jornada != 'todas' and 'Jornada' in df.columns:
            df = df[df['Jornada'].astype(str) == jornada]
        
        if posicion != 'todas' and 'Posicion' in df.columns:
            df = df[df['Posicion'] == posicion]
        
        if jugador != 'todos' and 'Jugador' in df.columns:
            df = df[df['Jugador'] == jugador]
        
        if df.empty:
            # Devolver figura vacía si no hay datos después de filtrar
            return go.Figure().update_layout(
                title="No hay datos disponibles para los filtros seleccionados",
                annotations=[
                    dict(
                        x=0.5,
                        y=0.5,
                        xref="paper",
                        yref="paper",
                        text="No hay datos para los filtros seleccionados",
                        showarrow=False,
                        font=dict(size=14)
                    )
                ]
            )
        
        # Crear gráficos según el tipo y los filtros aplicados
        if tipo_grafico == 'barras':
            # Para gráfico de barras
            
            # Determinar el eje x apropiado según los filtros aplicados
            if jugador != 'todos' and 'Jornada' in df.columns:
                # Si es un jugador específico, mostrar por jornada
                x_axis = 'Jornada'
                title = f"{estadistica} de {jugador} por Jornada"
            elif posicion != 'todas' and 'Jugador' in df.columns:
                # Si es por posición, mostrar por jugador
                x_axis = 'Jugador'
                title = f"{estadistica} por Jugador en posición {posicion}"
            elif jornada != 'todas' and 'Jugador' in df.columns:
                # Si es por jornada, mostrar por jugador
                x_axis = 'Jugador'
                title = f"{estadistica} por Jugador en Jornada {jornada}"
            elif 'Jugador' in df.columns:
                # Predeterminado: mostrar por jugador
                x_axis = 'Jugador'
                title = f"{estadistica} por Jugador"
            elif 'Jornada' in df.columns:
                # Si no hay jugadores, mostrar por jornada
                x_axis = 'Jornada'
                title = f"{estadistica} por Jornada"
            else:
                # Usar la primera columna como eje x
                x_axis = df.columns[0]
                title = f"{estadistica} por {x_axis}"
            
            # Ordenar datos para mejor visualización
            df_sorted = df.sort_values(by=[x_axis, estadistica])
            
            # Crear gráfico de barras
            fig = px.bar(
                df_sorted, 
                x=x_axis, 
                y=estadistica,
                title=title,
                text=estadistica,
                color='Posicion' if 'Posicion' in df.columns and x_axis != 'Posicion' else None,
                labels={estadistica: estadistica, x_axis: x_axis},
                color_discrete_sequence=['#0053A0', '#FFD700', '#FF4136', '#2ECC40', '#FF851B']
            )
            
            # Personalizar el diseño
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            )
            
            # Mejorar la presentación de las barras
            fig.update_traces(
                texttemplate='%{text}', 
                textposition='outside',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1
            )
            
        elif tipo_grafico == 'linea':
            # Para gráfico de línea
            
            # Determinar el eje x apropiado según los filtros aplicados
            if 'Jornada' in df.columns:
                # Si hay jornadas disponibles, usar como eje x
                x_axis = 'Jornada'
                group_by = 'Jugador' if 'Jugador' in df.columns and jugador == 'todos' else None
                title = f"Evolución de {estadistica} por Jornada"
            else:
                # Usar la primera columna como eje x
                x_axis = df.columns[0]
                group_by = None
                title = f"Evolución de {estadistica} por {x_axis}"
            
            # Ordenar datos para líneas continuas
            df_sorted = df.sort_values(by=x_axis)
            
            # Crear gráfico de línea
            fig = px.line(
                df_sorted, 
                x=x_axis, 
                y=estadistica,
                color=group_by,
                title=title,
                markers=True,
                labels={estadistica: estadistica, x_axis: x_axis},
                color_discrete_sequence=['#0053A0', '#FFD700', '#FF4136', '#2ECC40', '#FF851B']
            )
            
            # Personalizar el diseño
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            )
            
        elif tipo_grafico == 'pastel':
            # Para gráfico de pastel
            
            # Determinar cómo agrupar los datos
            if jugador != 'todos' and 'Jornada' in df.columns:
                # Si es un jugador específico, agrupar por jornada
                group_col = 'Jornada'
                title = f"Distribución de {estadistica} de {jugador} por Jornada"
            elif 'Jugador' in df.columns:
                # Agrupar por jugador
                group_col = 'Jugador'
                title = f"Distribución de {estadistica} por Jugador"
            elif 'Posicion' in df.columns:
                # Agrupar por posición
                group_col = 'Posicion'
                title = f"Distribución de {estadistica} por Posición"
            else:
                # Usar la primera columna
                group_col = df.columns[0]
                title = f"Distribución de {estadistica} por {group_col}"
            
            # Agrupar y sumar la estadística
            df_agg = df.groupby(group_col)[estadistica].sum().reset_index()
            
            # Crear gráfico de pastel
            fig = px.pie(
                df_agg,
                values=estadistica,
                names=group_col,
                title=title,
                color_discrete_sequence=['#0053A0', '#FFD700', '#FF4136', '#2ECC40', '#FF851B']
            )
            
            # Personalizar el diseño
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif"),
            )
            
            # Personalizar el texto
            fig.update_traces(
                textinfo='percent+label',
                pull=[0.05] * len(df_agg),
                marker=dict(line=dict(color='#FFFFFF', width=2))
            )
            
        elif tipo_grafico == 'dispersion':
            # Para gráfico de dispersión
            
            # Determinar las columnas a utilizar
            if 'Tiempo' in df.columns and estadistica != 'Tiempo':
                # Relacionar tiempo jugado con la estadística seleccionada
                x_col = 'Tiempo'
                y_col = estadistica
                title = f"Relación entre Tiempo Jugado y {estadistica}"
            elif 'GF' in df.columns and estadistica != 'GF':
                # Relacionar goles con la estadística seleccionada
                x_col = 'GF'
                y_col = estadistica
                title = f"Relación entre Goles y {estadistica}"
            else:
                # Usar estadística seleccionada y jornada si está disponible
                y_col = estadistica
                if 'Jornada' in df.columns:
                    x_col = 'Jornada'
                    title = f"{estadistica} vs Jornada"
                else:
                    # Si no hay columnas adecuadas, usar la primera columna numérica diferente de la estadística
                    numeric_cols = [col for col in df.select_dtypes(include=['number']).columns if col != estadistica]
                    x_col = numeric_cols[0] if numeric_cols else df.columns[0]
                    title = f"{estadistica} vs {x_col}"
            
            # Crear gráfico de dispersión
            fig = px.scatter(
                df, 
                x=x_col, 
                y=y_col,
                color='Jugador' if 'Jugador' in df.columns else None,
                size='Dorsal' if 'Dorsal' in df.columns else None,
                title=title,
                labels={x_col: x_col, y_col: y_col},
                hover_name='Jugador' if 'Jugador' in df.columns else None,
                hover_data=['Posicion'] if 'Posicion' in df.columns else None,
                color_discrete_sequence=['#0053A0', '#FFD700', '#FF4136', '#2ECC40', '#FF851B']
            )
            
            # Personalizar el diseño
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Arial, sans-serif"),
                xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            )
        
        return fig
    
    # Callback para actualizar el resumen
    @app.callback(
        Output('resumen-estadisticas', 'children'),
        [Input('stored-estadisticas-data', 'data'),
         Input('jornada-dropdown', 'value'),
         Input('posicion-dropdown', 'value'),
         Input('jugador-dropdown', 'value')]
    )
    def actualizar_resumen_estadisticas(stored_data, jornada, posicion, jugador):
        """Genera un resumen de estadísticas basado en los datos y filtros aplicados"""
        if not stored_data or stored_data.get('error') or not stored_data.get('data'):
            return html.Div(className="alert alert-warning", children=[
                html.I(className="fas fa-info-circle me-2"),
                "No hay datos disponibles para generar el resumen."
            ])
        
        try:
            df = pd.DataFrame(stored_data['data'])
            
            # Aplicar filtros si las columnas existen
            if jornada != 'todas' and 'Jornada' in df.columns:
                df = df[df['Jornada'].astype(str) == jornada]
            
            if posicion != 'todas' and 'Posicion' in df.columns:
                df = df[df['Posicion'] == posicion]
            
            if jugador != 'todos' and 'Jugador' in df.columns:
                df = df[df['Jugador'] == jugador]
            
            if df.empty:
                return html.Div(className="alert alert-warning", children=[
                    html.I(className="fas fa-info-circle me-2"),
                    "No hay datos disponibles para los filtros seleccionados."
                ])
            
            # Crear un resumen estadístico según los datos disponibles
            resumen_cards = []
            
            # Si hay datos específicos del jugador
            if jugador != 'todos' and 'Jugador' in df.columns:
                stats = []
                
                # Tiempo total
                if 'Tiempo' in df.columns:
                    tiempo_total = df['Tiempo'].sum()
                    stats.append(html.P(f"Tiempo total jugado: {tiempo_total} minutos"))
                
                # Partidos jugados
                if 'Jornada' in df.columns:
                    partidos = len(df['Jornada'].unique())
                    stats.append(html.P(f"Partidos jugados: {partidos}"))
                
                # Goles
                if 'GF' in df.columns:
                    goles = df['GF'].sum()
                    stats.append(html.P(f"Goles: {goles}"))
                
                # Asistencias
                if 'Asist' in df.columns:
                    asistencias = df['Asist'].sum()
                    stats.append(html.P(f"Asistencias: {asistencias}"))
                
                # Tarjetas
                if 'TA' in df.columns:
                    ta = df['TA'].sum()
                    stats.append(html.P(f"Tarjetas amarillas: {ta}"))
                
                if 'TR' in df.columns:
                    tr = df['TR'].sum()
                    stats.append(html.P(f"Tarjetas rojas: {tr}"))
                
                # Añadir tarjeta de resumen
                if stats:
                    resumen_cards.append(
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader(f"Resumen de {jugador}", className="text-center fw-bold"),
                                dbc.CardBody(stats)
                            ], color="primary", outline=True)
                        ], width=12, className="mb-3")
                    )
            
            # Si estamos viendo datos de varios jugadores
            elif 'Jugador' in df.columns:
                # Calcular totales por posición si están disponibles
                if 'Posicion' in df.columns:
                    posiciones_cards = []
                    posiciones = df['Posicion'].unique()
                    
                    for pos in posiciones:
                        df_pos = df[df['Posicion'] == pos]
                        stats_pos = []
                        
                        # Jugadores en esta posición
                        jugadores_count = len(df_pos['Jugador'].unique())
                        stats_pos.append(html.P(f"Jugadores: {jugadores_count}"))
                        
                        # Tiempo total
                        if 'Tiempo' in df.columns:
                            tiempo_total = df_pos['Tiempo'].sum()
                            stats_pos.append(html.P(f"Tiempo total: {tiempo_total} min"))
                        
                        # Goles
                        if 'GF' in df.columns:
                            goles = df_pos['GF'].sum()
                            stats_pos.append(html.P(f"Goles: {goles}"))
                        
                        # Asistencias
                        if 'Asist' in df.columns:
                            asistencias = df_pos['Asist'].sum()
                            stats_pos.append(html.P(f"Asistencias: {asistencias}"))
                        
                        posiciones_cards.append(
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(f"Posición: {pos}", className="text-center fw-bold"),
                                    dbc.CardBody(stats_pos)
                                ], color="info", outline=True)
                            ], width=12, md=4, className="mb-3")
                        )
                    
                    # Añadir tarjetas de posiciones
                    if posiciones_cards:
                        resumen_cards.append(dbc.Row(posiciones_cards, className="mt-3"))
                
                # Mostrar jugadores destacados
                if 'GF' in df.columns and df['GF'].sum() > 0:
                    # Top goleadores
                    goleadores = df.groupby('Jugador')['GF'].sum().reset_index().sort_values('GF', ascending=False).head(5)
                    
                    if not goleadores.empty:
                        tabla_goleadores = dash_table.DataTable(
                            columns=[
                                {"name": "Jugador", "id": "Jugador"},
                                {"name": "Goles", "id": "GF"}
                            ],
                            data=goleadores.to_dict('records'),
                            style_header={
                                'backgroundColor': '#0053A0',
                                'color': 'white',
                                'fontWeight': 'bold'
                            },
                            style_cell={'textAlign': 'left'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f5f5f5'
                                }
                            ],
                        )
                        
                        resumen_cards.append(
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Top Goleadores", className="text-center fw-bold"),
                                    dbc.CardBody([tabla_goleadores])
                                ], color="success", outline=True)
                            ], width=12, md=6, className="mb-3")
                        )
                
                if 'Asist' in df.columns and df['Asist'].sum() > 0:
                    # Top asistentes
                    asistentes = df.groupby('Jugador')['Asist'].sum().reset_index().sort_values('Asist', ascending=False).head(5)
                    
                    if not asistentes.empty:
                        tabla_asistentes = dash_table.DataTable(
                            columns=[
                                {"name": "Jugador", "id": "Jugador"},
                                {"name": "Asistencias", "id": "Asist"}
                            ],
                            data=asistentes.to_dict('records'),
                            style_header={
                                'backgroundColor': '#0053A0',
                                'color': 'white',
                                'fontWeight': 'bold'
                            },
                            style_cell={'textAlign': 'left'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': '#f5f5f5'
                                }
                            ],
                        )
                        
                        resumen_cards.append(
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Top Asistentes", className="text-center fw-bold"),
                                    dbc.CardBody([tabla_asistentes])
                                ], color="success", outline=True)
                            ], width=12, md=6, className="mb-3")
                        )
            
            # Resumen general independientemente de los filtros
            stats_generales = []
            
            # Total jugadores
            if 'Jugador' in df.columns:
                total_jugadores = len(df['Jugador'].unique())
                stats_generales.append(html.P(f"Total jugadores: {total_jugadores}"))
            
            # Total jornadas
            if 'Jornada' in df.columns:
                total_jornadas = len(df['Jornada'].unique())
                stats_generales.append(html.P(f"Total jornadas: {total_jornadas}"))
            
            # Totales de estadísticas
            if 'GF' in df.columns:
                total_goles = df['GF'].sum()
                stats_generales.append(html.P(f"Total goles: {total_goles}"))
            
            if 'Asist' in df.columns:
                total_asistencias = df['Asist'].sum()
                stats_generales.append(html.P(f"Total asistencias: {total_asistencias}"))
            
            if 'TA' in df.columns and 'TR' in df.columns:
                total_ta = df['TA'].sum()
                total_tr = df['TR'].sum()
                stats_generales.append(html.P(f"Tarjetas: {total_ta} amarillas, {total_tr} rojas"))
            
            # Añadir tarjeta de resumen general
            if stats_generales:
                resumen_cards.insert(0, 
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Resumen General", className="text-center fw-bold"),
                            dbc.CardBody(stats_generales)
                        ], color="primary", outline=True)
                    ], width=12, className="mb-3")
                )
            
            # Si no hay tarjetas, mostrar mensaje
            if not resumen_cards:
                return html.Div(className="alert alert-info", children=[
                    html.I(className="fas fa-info-circle me-2"),
                    "No hay suficientes datos para generar un resumen detallado."
                ])
            
            return dbc.Row(resumen_cards)
            
        except Exception as e:
            print(f"Error al generar resumen: {e}")
            return html.Div(className="alert alert-danger", children=[
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Error al generar el resumen: {str(e)}"
            ])