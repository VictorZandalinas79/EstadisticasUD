"""
Funciones para interactuar con la base de datos MySQL
"""
import mysql.connector
from config import DB_CONFIG

def execute_query(query, params=None):
    """
    Ejecuta una consulta SQL y devuelve los resultados
    
    Args:
        query (str): Consulta SQL a ejecutar
        params (tuple, optional): Parámetros para la consulta
    
    Returns:
        list: Lista de diccionarios con los resultados, o None si hay error
    """
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
        print(f"Error al ejecutar la consulta: {err}")
        return None
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def get_all_matches_data():
    """
    Obtiene los datos de todos los partidos con sus métricas de rendimiento
    
    Returns:
        list: Lista de diccionarios con la información de los partidos y métricas
    """
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
    
    # Para propósitos de depuración, agrega un print
    print("Ejecutando consulta para obtener datos de partidos...")
    
    # Ejecutar la consulta
    results = execute_query(query)
    
    # Comprobar si hay resultados
    if results:
        print(f"Se encontraron {len(results)} registros")
    else:
        print("No se obtuvieron datos o hubo un error en la consulta")
    
    return results

# Función para obtener datos simulados (usar en caso de que la BD no esté disponible)
def get_dummy_match_data():
    """
    Genera datos simulados para pruebas cuando la base de datos no está disponible
    
    Returns:
        list: Lista de diccionarios simulando datos de partidos
    """
    import random
    from datetime import datetime, timedelta
    
    dummy_data = []
    start_date = datetime(2023, 9, 1)
    
    # Generar datos para 10 partidos
    for i in range(1, 11):
        match_date = start_date + timedelta(days=i*14)
        is_league = random.random() > 0.3  # 70% probabilidad de ser partido de liga
        
        # Determinar el tipo y número de partido
        match_type = 'Liga' if is_league else 'Copa'
        match_number = i if is_league else i//2 + 1
        match_id = f"{'J' if is_league else 'C'}{match_number}"
        
        # Generar métricas aleatorias
        blp_won = random.randint(3, 15)
        blp_lost = random.randint(2, 10)
        blp_total = blp_won + blp_lost
        
        blr_won = random.randint(3, 12)
        blr_lost = random.randint(2, 8)
        blr_total = blr_won + blr_lost
        
        ptp_success = random.randint(5, 20)
        ptp_fail = random.randint(3, 15)
        ptp_total = ptp_success + ptp_fail
        
        ret_success = random.randint(8, 25)
        ret_fail = random.randint(5, 15)
        ret_total = ret_success + ret_fail
        
        oc_success = random.randint(6, 18)
        oc_fail = random.randint(4, 12)
        oc_total = oc_success + oc_fail
        
        vd_success = random.randint(10, 30)
        vd_fail = random.randint(5, 20)
        vd_total = vd_success + vd_fail
        
        ocas_atz = random.randint(2, 8)
        ocas_rival = random.randint(1, 6)
        
        # Calcular porcentajes
        blp_pct = round((blp_won * 100.0) / blp_total, 2) if blp_total else 0
        blr_pct = round((blr_won * 100.0) / blr_total, 2) if blr_total else 0
        ptp_pct = round((ptp_success * 100.0) / ptp_total, 2) if ptp_total else 0
        ret_pct = round((ret_success * 100.0) / ret_total, 2) if ret_total else 0
        oc_pct = round((oc_success * 100.0) / oc_total, 2) if oc_total else 0
        vd_pct = round((vd_success * 100.0) / vd_total, 2) if vd_total else 0
        
        # Construir registro
        match_record = {
            'match': match_id,
            'fecha': match_date.strftime('%d/%m/%Y'),
            'descripcion': f"{'UD Atzeneta vs Rival ' + str(i) if i % 2 == 0 else 'Rival ' + str(i) + ' vs UD Atzeneta'}",
            'match_type': match_type,
            'match_number': match_number,
            # BLP
            'won_balls_blp': blp_won,
            'lost_balls_blp': blp_lost,
            'total_balls_blp': blp_total,
            'blp_percentage': blp_pct,
            # BLR
            'won_balls_blr': blr_won,
            'lost_balls_blr': blr_lost,
            'total_balls_blr': blr_total,
            'blr_percentage': blr_pct,
            # PTP
            'success_ptp': ptp_success,
            'fail_ptp': ptp_fail,
            'total_ptp': ptp_total,
            'ptp_percentage': ptp_pct,
            # RET
            'success_ret': ret_success,
            'fail_ret': ret_fail,
            'total_ret': ret_total,
            'ret_percentage': ret_pct,
            # OC
            'success_oc': oc_success,
            'fail_oc': oc_fail,
            'total_oc': oc_total,
            'oc_percentage': oc_pct,
            # VD
            'success_vd': vd_success,
            'fail_vd': vd_fail,
            'total_vd': vd_total,
            'vd_percentage': vd_pct,
            # Ocasiones
            'ocas_atz': ocas_atz,
            'ocas_rival': ocas_rival,
            'dif_ocas': ocas_atz - ocas_rival
        }
        
        dummy_data.append(match_record)
    
    return dummy_data