import dash
from dash import html, dcc, dash_table, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import mysql.connector
import os
from flask import Flask

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'dbeastbengal2324.cfo6g0og0ypz.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Villafranca.06',
    'database': 'UDAtzeneta',
    'charset': 'utf8mb4',
    'port': 3306
}

# Inicializar la aplicación Dash
server = Flask(__name__)  # Primero crear el servidor Flask
app = dash.Dash(
    __name__, 
    server=server,  # Usar el servidor Flask creado
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title='UD Atzeneta Análisis',  # Título que aparecerá en la pestaña
    update_title=None  # Evita que aparezca "Updating..." cuando se actualiza la página
)

# Configurar el favicon (el icono)
app._favicon = 'escudo.png'  # Asegúrate de que escudo.png esté en la carpeta assets

# Añadir aquí el health check
@server.route('/health')
def health_check():
    return 'OK'

# Función para ejecutar consultas
def execute_query(query, params=None):
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Función para obtener datos
def get_all_matches_data():
   query = """
   WITH MatchStats AS (
       SELECT 
           `match`,
           STR_TO_DATE(fecha, '%d/%m/%Y') as fecha_parsed,
           fecha as fecha_original,
           team,
           idcode,
           idgroup,
           idtext,
           descripcion,
           CASE 
               WHEN SUBSTRING(`match`, 1, 1) = 'J' THEN 'Liga'
               WHEN SUBSTRING(`match`, 1, 1) = 'C' THEN 'Copa'
           END as match_type,
           CASE
               WHEN SUBSTRING(`match`, 1, 1) = 'J' THEN CAST(SUBSTRING(`match`, 2) AS SIGNED)
               WHEN SUBSTRING(`match`, 1, 1) = 'C' THEN CAST(SUBSTRING(`match`, 2) AS SIGNED)
           END as match_number
       FROM bot_events
       WHERE SUBSTRING(`match`, 1, 1) IN ('J', 'C')
   ),
   BallPossession AS (
       SELECT 
           ms.`match`,
           ms.fecha_parsed,
           ms.fecha_original,
           ms.match_type,
           ms.match_number,
           MAX(ms.descripcion) as descripcion,
           -- BLP (Balón Largo Propio)
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo propio' 
                     AND ms.idgroup = '2ª jugada'
                     AND ms.idtext = 'Ganada'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as won_balls_blp,
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo propio'
                     AND ms.idgroup = '2ª jugada'
                     AND ms.idtext = 'Perdida'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as lost_balls_blp,
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo propio'
                     AND ms.idgroup = '2ª jugada'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as total_balls_blp,
           -- BLR (Balón Largo Rival)
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo rival' 
                     AND ms.idgroup = '2ª jugada'
                     AND ms.idtext = 'Ganada'
                     AND ms.team != 'UD Atzeneta' THEN 1 END) as won_balls_blr,
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo rival'
                     AND ms.idgroup = '2ª jugada'
                     AND ms.idtext = 'Perdida'
                     AND ms.team != 'UD Atzeneta' THEN 1 END) as lost_balls_blr,
           COUNT(CASE WHEN ms.idcode = 'Tras balon largo rival'
                     AND ms.idgroup = '2ª jugada'
                     AND ms.team != 'UD Atzeneta' THEN 1 END) as total_balls_blr,
           -- PTP (Presión Tras Pérdida)
           COUNT(CASE WHEN ms.idcode = 'Presión tras perdida' 
                     AND ms.idgroup = 'Presión conjunta'
                     AND ms.idtext = 'Si'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as success_ptp,
           COUNT(CASE WHEN ms.idcode = 'Presión tras perdida'
                     AND ms.idgroup = 'Presión conjunta'
                     AND ms.idtext = 'No'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as fail_ptp,
           COUNT(CASE WHEN ms.idcode = 'Presión tras perdida'
                     AND ms.idgroup = 'Presión conjunta'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as total_ptp,
           -- RET (Retornos)
           COUNT(CASE WHEN ms.idcode = 'Retornos' 
                     AND ms.idgroup = 'Retorno conjunto'
                     AND ms.idtext = 'Si'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as success_ret,
           COUNT(CASE WHEN ms.idcode = 'Retornos'
                     AND ms.idgroup = 'Retorno conjunto'
                     AND ms.idtext = 'No'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as fail_ret,
           COUNT(CASE WHEN ms.idcode = 'Retornos'
                     AND ms.idgroup = 'Retorno conjunto'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as total_ret,
           -- OC (Ocupación de Centros)
           COUNT(CASE WHEN ms.idcode = 'Ocupación del área centros' 
                     AND ms.idgroup = 'Buena ocupación'
                     AND ms.idtext = 'Si'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as success_oc,
           COUNT(CASE WHEN ms.idcode = 'Ocupación del área centros'
                     AND ms.idgroup = 'Buena ocupación'
                     AND ms.idtext = 'No'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as fail_oc,
           COUNT(CASE WHEN ms.idcode = 'Ocupación del área centros'
                     AND ms.idgroup = 'Buena ocupación'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as total_oc,
           -- VD (Vigilancias Defensivas)
           COUNT(CASE WHEN ms.idcode = 'Vigilancias Defensivas' 
                     AND ms.idgroup = 'Rivales controlados'
                     AND ms.idtext = 'Si'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as success_vd,
           COUNT(CASE WHEN ms.idcode = 'Vigilancias Defensivas'
                     AND ms.idgroup = 'Rivales controlados'
                     AND ms.idtext = 'No'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as fail_vd,
           COUNT(CASE WHEN ms.idcode = 'Vigilancias Defensivas'
                     AND ms.idgroup = 'Rivales controlados'
                     AND ms.team = 'UD Atzeneta' THEN 1 END) as total_vd,
           -- Ocasiones Atz
           COUNT(CASE WHEN ms.idcode = 'Xg' 
                   AND ms.idtext IN ('Ocasión clarisima', 'Ocasión Clara', 'Remate sin importancia')
                   AND ms.team = 'UD Atzeneta' THEN 1 END) as ocas_atz,
           -- Ocasiones Rival
           COUNT(CASE WHEN ms.idcode = 'Xg' 
                   AND ms.idtext IN ('Ocasión clarisima', 'Ocasión Clara', 'Remate sin importancia')
                   AND ms.team != 'UD Atzeneta' THEN 1 END) as ocas_rival
       FROM MatchStats ms
       GROUP BY ms.`match`, ms.fecha_parsed, ms.fecha_original, ms.match_type, ms.match_number
   )
   SELECT 
       `match`,
       fecha_original as fecha,
       descripcion,
       match_type,
       match_number,
       -- BLP stats
       won_balls_blp,
       lost_balls_blp,
       total_balls_blp,
       ROUND((won_balls_blp * 100.0) / NULLIF(total_balls_blp, 0), 2) as blp_percentage,
       -- BLR stats
       won_balls_blr,
       lost_balls_blr,
       total_balls_blr,
       ROUND((won_balls_blr * 100.0) / NULLIF(total_balls_blr, 0), 2) as blr_percentage,
       -- PTP stats
       success_ptp,
       fail_ptp,
       total_ptp,
       ROUND((success_ptp * 100.0) / NULLIF(total_ptp, 0), 2) as ptp_percentage,
       -- RET stats
       success_ret,
       fail_ret,
       total_ret,
       ROUND((success_ret * 100.0) / NULLIF(total_ret, 0), 2) as ret_percentage,
       -- OC stats
       success_oc,
       fail_oc,
       total_oc,
       ROUND((success_oc * 100.0) / NULLIF(total_oc, 0), 2) as oc_percentage,
       -- VD stats
       success_vd,
       fail_vd,
       total_vd,
       ROUND((success_vd * 100.0) / NULLIF(total_vd, 0), 2) as vd_percentage,
       -- Ocasiones stats
       ocas_atz,
       ocas_rival,
       (ocas_atz - ocas_rival) as dif_ocas
   FROM BallPossession
   ORDER BY fecha_parsed ASC;
   """
   return execute_query(query)

def create_evolution_table():
    # Obtener datos
    data = get_all_matches_data()
    
    # Convertir a DataFrame y ordenar por fecha
    df = pd.DataFrame(data)
    df['fecha_parsed'] = pd.to_datetime(df['fecha'])  # Detectará automáticamente el formato ISO
    df = df.sort_values('fecha_parsed')
    
    if not df.empty:
        metrics_rows = []
        style_conditions = []
        header_styles = []
        
        def get_match_description(row):
            tipo = 'J' if row['match_type'] == 'Liga' else 'C'
            desc = row['descripcion'] if pd.notna(row['descripcion']) else ''
            # Convertir la fecha al formato deseado para mostrar
            fecha_display = row['fecha_parsed'].strftime('%d/%m/%Y')
            return f"{desc}\n{tipo}{row['match_number']}\n({fecha_display})"

        for metric in ['BLP %', 'BLR %', 'PTP %', 'RET %', 'OC %', 'VD %', 'Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
            metric_row = {'Métrica': metric}
            columnas_orden = []
            partidos_grupo = []
            
            # Iterar sobre el DataFrame ordenado por fecha
            for _, row in df.iterrows():
                tipo = 'J' if row['match_type'] == 'Liga' else 'C'
                fecha_display = row['fecha_parsed'].strftime('%d/%m/%Y')
                # Crear ID de columna que incluya la fecha para mantener el orden
                columna_id = f"{row['fecha_parsed'].strftime('%Y%m%d')}_{tipo}{row['match_number']}"
                
                if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                    # Para métricas de ocasiones, usar el valor directamente
                    valor = row['ocas_atz'] if metric == 'Ocas Atz' else \
                            row['ocas_rival'] if metric == 'Ocas Rival' else \
                            row['dif_ocas']
                    if valor is None:
                        valor = 0
                    metric_row[columna_id] = f"{int(valor)}"  # Sin decimales
                    
                    # Estilos específicos para ocasiones
                    color = 'rgb(200, 200, 200)'  # Color neutral por defecto
                    if metric == 'Dif Ocas':
                        color = 'rgb(0, 255, 0)' if valor > 0 else 'rgb(255, 0, 0)' if valor < 0 else 'rgb(200, 200, 200)'
                    
                    style_conditions.append({
                        'if': {
                            'column_id': columna_id,
                            'filter_query': '{Métrica} = "' + metric + '"'
                        },
                        'backgroundColor': color,
                        'color': 'black'
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
                    'font-size': '10px'
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
        
        return dash_table.DataTable(
            id='evolution-table',
            columns=columns,
            data=final_df.to_dict('records'),
            style_table={
                'width': '100%',
                'overflowX': 'auto',
                'maxWidth': '100vw',  # Usa el ancho total disponible
                'fontSize': '0.9rem'   # Reduce ligeramente el tamaño de fuente
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
                'textAlign': 'center',
                'whiteSpace': 'pre-line',
                'padding': '5px',      # Reducido el padding
                'height': 'auto',
                'fontSize': '0.85rem'  # Texto ligeramente más pequeño en encabezados
            },
            style_cell={
                'textAlign': 'center',
                'padding': '5px',      # Reducido el padding
                'minWidth': '80px',    # Reducido el ancho mínimo
                'maxWidth': '150px',   # Reducido el ancho máximo
                'whiteSpace': 'normal',
                'height': 'auto',
                'fontSize': '0.9rem'   # Tamaño de fuente consistente
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'Métrica'},
                    'minWidth': '100px',
                    'width': '100px',
                    'maxWidth': '100px',
                }
            ],
            style_data_conditional=style_conditions,
            style_header_conditional=header_styles,
            markdown_options={'html': True},
            css=[{
                'selector': '.dash-table-container',
                'rule': 'margin: 0 auto; max-width: 100%; font-size: 0.9rem;'
            }]
        )
    return html.Div("No hay datos disponibles")

def get_color_scale(value):
    """
    Retorna un color basado en el valor del porcentaje:
    - Verde (más intenso cuanto más alto) para valores >= 60
    - Naranja a rojo para valores < 60
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
    
def generar_analisis_kpis(df):
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

# Layout principal
app.layout = html.Div([
    # Imagen de fondo
    html.Div(
        style={
            'position': 'fixed',
            'width': '100%',
            'height': '100%',
            'top': 0,
            'left': 0,
            'zIndex': -1,
            'backgroundImage': 'url("/assets/fondo_udatzeneta.png")',
            'backgroundSize': 'cover',
            'backgroundPosition': 'center',
            'backgroundRepeat': 'no-repeat',
            'opacity': '0.15'
        }
    ),
    dbc.Container([
       # Componente de actualización automática
       dcc.Interval(
           id='interval-component',
           interval=30*1000,  # actualiza cada 30 segundos
           n_intervals=0
       ),
       
       # Añadir el escudo
       html.Img(
           src='/assets/escudo.png',
           style={
               'height': '80px',
               'display': 'block',
               'margin': 'auto',
               'marginBottom': '15px'
           }
       ),
       
       html.H1("UD Atzeneta Analytics", 
               className="text-center my-3",
               style={'fontSize': '2rem'}),
       
       # Tarjeta informativa
       dbc.Card([
           dbc.CardBody([
               html.H4("KPI", className="card-title", style={'fontSize': '1.5rem'}),
               html.P(
                   "métricas que permiten medir y determinar la efectividad y rentabilidad de nuestro equipo "
                   ", UD Atzeneta",
                   className="card-text",
                   style={'fontSize': '0.9rem'}
               )
           ])
       ], className="mb-3"),
       
       # Tabla de evolución
       # Tabla de evolución
html.Div([
    dash_table.DataTable(
        id='evolution-table',
        style_table={
            'width': '100%',
            'overflowX': 'auto',
            'maxWidth': '100vw',
            'fontSize': '0.9rem',
            'position': 'relative'  # Necesario para columna fija
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
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
                'position': 'sticky',
                'left': 0,
                'backgroundColor': 'white',
                'zIndex': 1
            }
        ],
        markdown_options={'html': True}
    )
], className="mb-3", style={'overflowX': 'auto', 'width': '100%'}),
       
       # Análisis automático con loading
       dbc.Card([
           dbc.CardBody([
               html.H4("Análisis Automático", 
                      className="card-title",
                      style={'fontSize': '1.5rem'}),
               dcc.Loading(
                   id="loading-analysis",
                   type="default",
                   children=html.Div(id='analisis-automatico')
               )
           ])
       ], className="mb-3"),
       
   ], fluid=True, className="px-2")
], style={'maxWidth': '100vw', 'overflow': 'hidden'})

# Y justo después del layout, añade los callbacks:
@app.callback(
   Output('analisis-automatico', 'children'),
   [Input('evolution-table', 'data'),
    Input('interval-component', 'n_intervals')]
)
def update_analisis(data, n_intervals):
   if not data:
       return "No hay datos para analizar"
   
   df = pd.DataFrame(data)
   return generar_analisis_kpis(df)

# Nuevo callback para actualizar la tabla automáticamente
@app.callback(
   [Output('evolution-table', 'data'),
    Output('evolution-table', 'columns'),
    Output('evolution-table', 'style_data_conditional'),
    Output('evolution-table', 'style_header_conditional')],
   Input('interval-component', 'n_intervals')
)
def update_table_data(n_intervals):
    print(f"Actualizando datos: {n_intervals}")  # Para ver en los logs cuando se actualiza
    data = get_all_matches_data()
    if data:
        df = pd.DataFrame(data)
        df['fecha_parsed'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha_parsed')
        
        metrics_rows = []
        style_conditions = []
        header_styles = []
        
        def get_match_description(row):
            tipo = 'J' if row['match_type'] == 'Liga' else 'C'
            desc = row['descripcion'] if pd.notna(row['descripcion']) else ''
            fecha_display = row['fecha_parsed'].strftime('%d/%m/%Y')
            return f"{desc}\n{tipo}{row['match_number']}\n({fecha_display})"

        for metric in ['BLP %', 'BLR %', 'PTP %', 'RET %', 'OC %', 'VD %', 'Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
            metric_row = {'Métrica': metric}
            columnas_orden = []
            partidos_grupo = []
            
            # Iterar sobre el DataFrame ordenado por fecha
            for _, row in df.iterrows():
                tipo = 'J' if row['match_type'] == 'Liga' else 'C'
                fecha_display = row['fecha_parsed'].strftime('%d/%m/%Y')
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
                    'font-size': '10px'
                })
                
                # Después de cada 5 partidos
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
                    metric_row[media_col] = f"{media:.2f}%"  # Con % para el resto
                columnas_orden.append(media_col)
            
            # Media total
            valores_totales = []
            for columna in metric_row.keys():
                if columna not in ['Métrica', 'Media Total']:
                    try:
                        if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                            # Para métricas de ocasiones, tomar el valor directo sin strip
                            valores_totales.append(float(metric_row[columna]))
                        else:
                            # Para el resto de métricas, quitar el %
                            valores_totales.append(float(metric_row[columna].strip('%')))
                    except (ValueError, AttributeError):
                        continue

            if valores_totales:
                media_total = sum(valores_totales) / len(valores_totales)
                if metric in ['Ocas Atz', 'Ocas Rival', 'Dif Ocas']:
                    # Para métricas de ocasiones, sin %
                    metric_row['Media Total'] = f"{int(round(media_total))}"
                else:
                    # Para el resto de métricas, con %
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
    return [], [], [], []

if __name__ == '__main__':
   port = int(os.environ.get('PORT', 10000))
   app.run_server(
       host='0.0.0.0',
       port=port,
       debug=False
   )