"""
Página principal (Home) con la tabla de KPIs y navegación superior
"""
from dash import html, dcc, dash_table, callback, Output, Input, State
import dash_bootstrap_components as dbc
import pandas as pd
from utils.database import get_all_matches_data
from config import AUTO_REFRESH_INTERVAL

# Layout de la página principal
def home_layout():
    """
    Crea el layout para la página principal
    """
    return dbc.Container([
        # Componente de actualización automática
        dcc.Interval(
            id='interval-component',
            interval=AUTO_REFRESH_INTERVAL,  # 30 segundos por defecto
            n_intervals=0
        ),
        
        # Encabezado - Movido arriba de los iconos
        dbc.Row([
            dbc.Col([
                html.H1("Panel de Control - KPIs", className="text-center my-4 fw-bold"),
                html.Hr(className="my-3")
            ])
        ]),
        
        # Navegación superior con iconos grandes y clicables
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            # Tarjeta para Corners
                            dbc.Col([
                                html.A(
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.Img(src="/assets/icono_corner.png", height="120px", className="mx-auto d-block mb-3"),
                                            html.H4("Corners", className="text-center m-0 fw-bold"),
                                        ], className="d-flex flex-column align-items-center justify-content-center h-100")
                                    ], className="h-100 shadow text-center", color="light", style={"cursor": "pointer", "transition": "transform 0.2s", ":hover": {"transform": "scale(1.05)"}})
                                , href="/corners", className="text-decoration-none d-block h-100")
                            ], md=4, className="mb-3"),
                            
                            # Tarjeta para Faltas
                            dbc.Col([
                                html.A(
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.Img(src="/assets/icono_falta.png", height="120px", className="mx-auto d-block mb-3"),
                                            html.H4("Faltas", className="text-center m-0 fw-bold"),
                                        ], className="d-flex flex-column align-items-center justify-content-center h-100")
                                    ], className="h-100 shadow text-center", color="light", style={"cursor": "pointer", "transition": "transform 0.2s", ":hover": {"transform": "scale(1.05)"}})
                                , href="/faltas", className="text-decoration-none d-block h-100")
                            ], md=4, className="mb-3"),
                            
                            # Tarjeta para Momentos de juego
                            dbc.Col([
                                html.A(
                                    dbc.Card([
                                        dbc.CardBody([
                                            html.Img(src="/assets/momentos_juego.jpg", height="120px", className="mx-auto d-block mb-3"),
                                            html.H4("Momentos de Juego", className="text-center m-0 fw-bold"),
                                        ], className="d-flex flex-column align-items-center justify-content-center h-100")
                                    ], className="h-100 shadow text-center", color="light", style={"cursor": "pointer", "transition": "transform 0.2s", ":hover": {"transform": "scale(1.05)"}})
                                , href="/momentosjuego", className="text-decoration-none d-block h-100")
                            ], md=4, className="mb-3"),
                        ], className="g-4")
                    ])
                ], className="mb-5")
            ])
        ]),
        
        # Tarjeta informativa (opcional - movida después de los iconos)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Indicadores Clave de Rendimiento", className="card-title mb-2"),
                        html.P(
                            "Esta tabla muestra los principales indicadores de rendimiento del equipo "
                            "UD Atzeneta a lo largo de la temporada.",
                            className="card-text"
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Tabla de KPIs
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Evolución por Partido", className="m-0")),
                    dbc.CardBody([
                        html.Div([
                            # La tabla se cargará mediante callback
                            dash_table.DataTable(
                                id='evolution-table',
                                style_table={
                                    'width': '100%',
                                    'overflowX': 'auto',
                                    'maxWidth': '100vw',
                                    'fontSize': '0.9rem'
                                },
                                style_header={
                                    'backgroundColor': 'rgb(30, 67, 137)',
                                    'color': 'white',
                                    'fontWeight': 'bold',
                                    'textAlign': 'center',
                                    'whiteSpace': 'pre-line',
                                    'padding': '5px',
                                    'height': 'auto',
                                    'fontSize': '0.85rem'
                                },
                                style_cell={
                                    'textAlign': 'center',
                                    'padding': '5px',
                                    'minWidth': '80px',
                                    'maxWidth': '150px',
                                    'whiteSpace': 'normal',
                                    'height': 'auto',
                                    'fontSize': '0.9rem'
                                },
                                style_cell_conditional=[
                                    {
                                        'if': {'column_id': 'Métrica'},
                                        'minWidth': '100px',
                                        'width': '100px',
                                        'maxWidth': '100px',
                                        'fontWeight': 'bold',
                                        'backgroundColor': 'rgb(240, 240, 240)',
                                    }
                                ],
                                markdown_options={'html': True},
                                tooltip_delay=0,
                                tooltip_duration=None
                            )
                        ], className="table-responsive")
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Análisis automático
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Análisis Automático", className="m-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-analysis",
                            type="circle",
                            children=html.Div(id='analisis-automatico')
                        )
                    ])
                ], className="mb-4")
            ])
        ]),
        
        # Botón para exportar informe PDF
        dbc.Row([
            dbc.Col([
                dbc.Button([
                    html.I(className="fas fa-file-pdf me-2"),
                    "Exportar Informe PDF"
                ], id="btn-export-pdf", color="success", className="float-end mb-4")
            ])
        ])
    ], fluid=True)

# Función para obtener el color según el valor del porcentaje
def get_color_scale(value):
    """
    Retorna un color basado en el valor del porcentaje:
    - Verde para valores >= 60%
    - Amarillo para valores entre 40% y 60%
    - Rojo para valores < 40%
    """
    if value >= 60:
        # Escala de verde: más intenso cuanto más alto sea el valor
        intensity = min(255, int(150 + (value - 60) * 2))
        return f'rgb(0, {intensity}, 0)'
    else:
        # Escala de naranja a rojo: más rojo cuanto más bajo sea el valor
        red = 255
        green = max(0, int(165 * (value / 60)))
        return f'rgb({red}, {green}, 0)'

# Función para obtener colores para las ocasiones
def get_color_scale_ocasiones(value, is_rival=False):
    """
    Retorna un color basado en el valor de las ocasiones:
    Para Ocas Atz y Dif Ocas:
    - Rojo para valores <= 0
    - Naranja para valores entre 1 y 4
    - Verde (más intenso cuanto más alto) para valores >= 5
    
    Para Ocas Rival (invertido):
    - Verde para valores <= 0
    - Naranja para valores entre 1 y 4
    - Rojo (más intenso cuanto más alto) para valores >= 5
    """
    if is_rival:
        # Escala invertida para ocasiones del rival
        if value <= 0:
            return 'rgb(0, 255, 0)'  # Verde
        elif value < 5:
            return 'rgb(255, 165, 0)'  # Naranja
        else:
            # Escala de rojo: más intenso cuanto más alto sea el valor
            intensity = min(255, int(150 + (value * 10)))
            return f'rgb({intensity}, 0, 0)'
    else:
        # Escala normal para ocasiones propias y diferencia
        if value <= 0:
            return 'rgb(255, 0, 0)'  # Rojo
        elif value < 5:
            return 'rgb(255, 165, 0)'  # Naranja
        else:
            # Escala de verde: más intenso cuanto más alto sea el valor
            intensity = min(255, int(150 + (value * 10)))
            return f'rgb(0, {intensity}, 0)'

# Función para formatear la tabla de evolución
def format_evolution_table(data):
    """
    Formatea los datos para la tabla de evolución
    
    Args:
        data (list): Lista de diccionarios con los datos de partidos
        
    Returns:
        tuple: (datos para la tabla, columnas, condiciones de estilo, estilos de encabezado)
    """
    if not data:
        return [], [], [], []
        
    df = pd.DataFrame(data)
    
    # Detectar y convertir fechas adecuadamente
    try:
        # Primero, verificar el formato real de las fechas
        sample_date = df['fecha'].iloc[0] if not df.empty else None
        print(f"Formato de fecha detectado: {sample_date}")
        
        # Intentar diferentes formatos según lo que veamos
        if sample_date and '-' in sample_date:  # formato ISO 'YYYY-MM-DD'
            df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d')
        else:  # formato original '%d/%m/%Y'
            df['fecha_parsed'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y')
            
    except Exception as e:
        print(f"Error al parsear fechas: {e}")
        # Fallback: intentar forzar el formato automático
        try:
            df['fecha_parsed'] = pd.to_datetime(df['fecha'], errors='coerce')
            # Verificar si tenemos fechas NaT (Not a Time)
            if df['fecha_parsed'].isna().any():
                print("Advertencia: Algunas fechas no pudieron ser parseadas correctamente")
        except:
            # Último recurso: crear fechas simuladas
            print("Creando fechas simuladas como último recurso")
            import datetime
            base_date = datetime.datetime(2023, 9, 1)
            df['fecha_parsed'] = [base_date + datetime.timedelta(days=i*14) for i in range(len(df))]
    
    # Ordenar por fecha
    df = df.sort_values('fecha_parsed')
    
    metrics_rows = []
    style_conditions = []
    header_styles = []
    
    def get_match_description(row):
        """
        Genera una descripción formateada del partido sin duplicar el código del partido
        
        Args:
            row: Fila del DataFrame con información del partido
            
        Returns:
            str: Descripción formateada del partido para el encabezado de columna
        """
        tipo = 'J' if row['match_type'] == 'Liga' else 'C'
        desc = row['descripcion'] if pd.notna(row['descripcion']) else ''
        fecha_display = row['fecha']
        
        # Verificamos si la descripción ya incluye el código del partido
        if desc and (f"{tipo}{row['match_number']}" in desc):
            # Si ya está incluido, solo mostramos la descripción y la fecha
            return f"{desc}({fecha_display})"
        else:
            # Si no está incluido, lo añadimos
            return f"{desc}{tipo}{row['match_number']}({fecha_display})"

    for metric in ['BLP %', 'BLR %', 'PTP %', 'RET %', 'OC %', 'VD %', 'Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
        metric_row = {'Métrica': metric}
        columnas_orden = []
        partidos_grupo = []
        
        # Iterar sobre el DataFrame ordenado por fecha
        for _, row in df.iterrows():
            tipo = 'J' if row['match_type'] == 'Liga' else 'C'
            columna_id = f"{row['fecha_parsed'].strftime('%Y%m%d')}_{tipo}{row['match_number']}"
            
            if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                # Para métricas de ocasiones, usar el valor directamente
                valor = row['ocas_atz'] if metric == 'Ocas Atz' else \
                        row['ocas_rival'] if metric == 'Ocas Rival' else \
                        row['dif_ocas']
                if valor is None:
                    valor = 0
                metric_row[columna_id] = f"{int(valor)}"  # Sin decimales
                
                # Determinar si es la métrica del rival
                is_rival = metric == 'Ocas Rival'
                
                style_conditions.append({
                    'if': {
                        'column_id': columna_id,
                        'filter_query': '{Métrica} = "' + metric + '"'
                    },
                    'backgroundColor': get_color_scale_ocasiones(float(valor), is_rival),
                    'color': 'white' if float(valor) >= 1 else 'black'
                })
            else:
                # El código existente para métricas de porcentaje
                if metric == 'BLP %':
                    porcentaje = row['blp_percentage']
                elif metric == 'BLR %':
                    porcentaje = row['blr_percentage']
                elif metric == 'PTP %':
                    porcentaje = row['ptp_percentage']
                elif metric == 'RET %':
                    porcentaje = row['ret_percentage']
                elif metric == 'OC %':
                    porcentaje = row['oc_percentage']
                else:  # VD %
                    porcentaje = row['vd_percentage']
                
                if porcentaje is None:
                    porcentaje = 0
                
                metric_row[columna_id] = f"{float(porcentaje):.2f}%"
                style_conditions.append({
                    'if': {
                        'column_id': columna_id,
                        'filter_query': '{Métrica} = "' + metric + '"'
                    },
                    'backgroundColor': get_color_scale(float(porcentaje)),
                    'color': 'white' if float(porcentaje) > 40 else 'black'
                })
            
            partidos_grupo.append(columna_id)
            
            header_styles.append({
                'if': {'column_id': columna_id},
                'backgroundColor': 'rgba(135, 206, 235, 0.7)' if tipo == 'J' else 'rgba(255, 165, 0, 0.7)',
                'font-size': '12px'
            })
            
            # Después de cada 5 partidos, añadir la media
            if len(partidos_grupo) == 5:
                columnas_orden.extend(partidos_grupo)
                if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                    valores = [float(metric_row[col]) for col in partidos_grupo]
                    media = sum(valores) / len(valores)
                    media_col = f'Media {len(columnas_orden)//5}'
                    metric_row[media_col] = f"{int(round(media))}"
                else:
                    valores = [float(metric_row[col].strip('%')) for col in partidos_grupo]
                    media = sum(valores) / len(valores)
                    media_col = f'Media {len(columnas_orden)//5}'
                    metric_row[media_col] = f"{media:.2f}%"
                columnas_orden.append(media_col)
                partidos_grupo = []
        
        # Procesar últimos partidos si quedan
        if partidos_grupo:
            columnas_orden.extend(partidos_grupo)
            if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                valores = [float(metric_row[col]) for col in partidos_grupo]
                media = sum(valores) / len(valores)
                media_col = f'Media {(len(columnas_orden)-len(partidos_grupo))//5 + 1}'
                metric_row[media_col] = f"{int(round(media))}"  # Sin % para ocasiones
            else:
                valores = [float(metric_row[col].strip('%')) for col in partidos_grupo]
                media = sum(valores) / len(valores)
                media_col = f'Media {(len(columnas_orden)-len(partidos_grupo))//5 + 1}'
                metric_row[media_col] = f"{media:.2f}%"
            columnas_orden.append(media_col)

        # Media total
        valores_totales = []
        for columna in metric_row.keys():
            if columna not in ['Métrica', 'Media Total']:
                try:
                    if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                        valores_totales.append(float(metric_row[columna]))
                    else:
                        valores_totales.append(float(metric_row[columna].strip('%')))
                except (ValueError, AttributeError):
                    continue

        if valores_totales:
            media_total = sum(valores_totales) / len(valores_totales)
            if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                metric_row['Media Total'] = f"{int(round(media_total))}"  # Sin % para ocasiones
            else:
                metric_row['Media Total'] = f"{media_total:.2f}%"
            columnas_orden.append('Media Total')
        
        metrics_rows.append(metric_row)
    
    # Crear DataFrame final con las columnas ordenadas
    final_df = pd.DataFrame(metrics_rows)
    final_df = final_df[['Métrica'] + columnas_orden]
    
    # Crear columnas con nombres personalizados
    columns = [{"name": "Métrica", "id": "Métrica"}]
    for col in columnas_orden:
        if "Media" in col:
            columns.append({"name": col, "id": col})
        else:
            match_info = next(row for _, row in df.iterrows() 
                            if col.split('_')[1] == f"{('J' if row['match_type'] == 'Liga' else 'C')}{row['match_number']}")
            columns.append({
                "name": get_match_description(match_info),
                "id": col
            })
    
    return final_df.to_dict('records'), columns, style_conditions, header_styles

# Función para generar el análisis automático
def generar_analisis_kpis(df):
    """
    Genera un análisis automático de los KPIs
    
    Args:
        df (DataFrame): DataFrame con los datos de métricas
    
    Returns:
        list: Lista de componentes HTML con el análisis
    """
    insights = []
    
    descripcion_metricas = {
        'BLP %': 'Balones Largos Propios ganados',
        'BLR %': 'Balones Largos Rivales ganados',
        'PTP %': 'Presión Tras Pérdida exitosa',
        'RET %': 'Retornos exitosos',
        'OC %': 'Ocupación del área en centros',
        'VD %': 'Vigilancias Defensivas efectivas'
    }
    
    for metric in ['BLP %', 'BLR %', 'PTP %', 'RET %', 'OC %', 'VD %']:
        valores = df[df['Métrica'] == metric].iloc[0]
        valores_partidos = []
        
        # Recopilar datos de partidos
        for columna, valor in valores.items():
            if columna != 'Métrica' and 'Media' not in columna:
                try:
                    valor_num = float(valor.strip('%'))
                    valores_partidos.append({
                        'partido': columna,
                        'valor': valor_num,
                        'tipo': 'Liga' if 'J' in columna else 'Copa'
                    })
                except (ValueError, AttributeError):
                    continue
        
        if valores_partidos:
            # Análisis estadístico
            valores_num = [v['valor'] for v in valores_partidos]
            media = sum(valores_num) / len(valores_num)
            maximo = max(valores_num)
            minimo = min(valores_num)
            ultimos_3 = valores_num[-3:] if len(valores_num) >= 3 else valores_num
            media_ultimos = sum(ultimos_3) / len(ultimos_3)
            
            # Generar análisis narrativo
            analisis = f"Análisis de {descripcion_metricas[metric]}:\n\n"
            
            # Tendencia general
            analisis += "📊 Tendencia General:\n"
            if media_ultimos > media + 5:
                analisis += "El equipo muestra una clara mejoría en las últimas jornadas. "
            elif media_ultimos < media - 5:
                analisis += "Se observa un descenso en el rendimiento reciente. "
            else:
                analisis += "El rendimiento se mantiene estable. "
            
            # Puntos destacables
            mejor_partido = max(valores_partidos, key=lambda x: x['valor'])
            peor_partido = min(valores_partidos, key=lambda x: x['valor'])
            
            analisis += f"\n\n🔍 Puntos Destacables:\n"
            analisis += f"- Mejor registro: {mejor_partido['valor']:.1f}% en {mejor_partido['partido']}\n"
            analisis += f"- Registro más bajo: {peor_partido['valor']:.1f}% en {peor_partido['partido']}\n"
            analisis += f"- Promedio general: {media:.1f}%\n"
            
            # Recomendaciones específicas
            analisis += "\n📈 Análisis y Recomendaciones:\n"
            if metric == 'BLP %':
                if media < 50:
                    analisis += "Se recomienda mejorar la preparación de los balones largos y la coordinación con los receptores. "
                if maximo - minimo > 30:
                    analisis += "Hay una gran variabilidad en el rendimiento que necesita estabilizarse. "
            elif metric == 'BLR %':
                if media < 45:
                    analisis += "Se sugiere trabajar en la anticipación y posicionamiento defensivo. "
            elif metric == 'PTP %':
                if media < 55:
                    analisis += "Es importante mejorar la reacción colectiva tras pérdida. "
            elif metric == 'RET %':
                if media < 50:
                    analisis += "Se recomienda trabajar en la organización defensiva y los retornos ordenados. "
            elif metric == 'OC %':
                if media < 60:
                    analisis += "Se recomienda mejorar la ocupación de espacios en el área durante los centros. "
                if maximo - minimo > 25:
                    analisis += "La variabilidad en la ocupación del área necesita ser más consistente. "
            elif metric == 'VD %':
                if media < 65:
                    analisis += "Es importante mejorar el control y seguimiento de los rivales en fase defensiva. "
                if media_ultimos < media:
                    analisis += "Se sugiere reforzar el trabajo de vigilancias defensivas en los entrenamientos. "
            
            insights.append(html.Div([
                html.H5(metric, className="text-primary"),
                html.P(analisis.split('\n\n')[0]),  # Tendencia general
                html.P(analisis.split('\n\n')[1]),  # Puntos destacables
                html.P(analisis.split('\n\n')[2]),  # Recomendaciones
            ], className="mb-4"))
    
    return insights

# Registrar callbacks para la página principal
def register_home_callbacks(app):
    """
    Registra los callbacks para la página principal
    """
    # Callback para actualizar la tabla
    @app.callback(
        [Output('evolution-table', 'data'),
         Output('evolution-table', 'columns'),
         Output('evolution-table', 'style_data_conditional'),
         Output('evolution-table', 'style_header_conditional')],
        [Input('interval-component', 'n_intervals')]
    )
    def update_table_data(n_intervals):
        """Actualiza la tabla de evolución"""
        data = get_all_matches_data()
        if data:
            return format_evolution_table(data)
        return [], [], [], []
    
    # Callback para actualizar el análisis automático
    @app.callback(
        Output('analisis-automatico', 'children'),
        [Input('evolution-table', 'data')]
    )
    def update_analysis(table_data):
        """Actualiza el análisis automático basado en los datos de la tabla"""
        if not table_data:
            return html.Div("No hay datos disponibles para realizar el análisis.")
        
        df = pd.DataFrame(table_data)
        return generar_analisis_kpis(df)
    
    # Callback para el botón de exportar PDF (simulado)
    @app.callback(
        Output('btn-export-pdf', 'n_clicks'),
        Input('btn-export-pdf', 'n_clicks'),
        prevent_initial_call=True
    )
    def export_pdf(n_clicks):
        """Simula la exportación a PDF"""
        if n_clicks:
            print("Generando reporte PDF...")
            # Aquí iría la lógica real para generar un PDF
            return 0
        return n_clicks