import mysql.connector
from ..config.db_config import DB_CONFIG

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

def get_league_matches_data():
    query = """
    WITH MatchStats AS (
        SELECT 
            match,
            fecha,
            team,
            idcode,
            idgroup,
            idtext,
            CASE 
                WHEN SUBSTRING(match, 1, 1) = 'J' THEN 'Liga'
                WHEN SUBSTRING(match, 1, 1) = 'C' THEN 'Copa'
                WHEN SUBSTRING(match, 1, 1) = 'A' THEN 'Amistoso'
            END as match_type,
            CAST(SUBSTRING(match, 2) AS SIGNED) as match_number
        FROM UDAtzeneta.bot_events
        WHERE SUBSTRING(match, 1, 1) = 'J'
    ),
    BallPossession AS (
        SELECT 
            match,
            fecha,
            match_type,
            match_number,
            COUNT(CASE WHEN idcode = 'Tras balon largo propio' 
                      AND idgroup = '2ª jugada'
                      AND idtext = 'Ganada'
                      AND team = 'UD Atzeneta' THEN 1 END) as won_balls,
            COUNT(CASE WHEN idcode = 'Tras balon largo propio'
                      AND idgroup = '2ª jugada'
                      AND idtext = 'Perdida'
                      AND team = 'UD Atzeneta' THEN 1 END) as lost_balls,
            COUNT(CASE WHEN idcode = 'Tras balon largo propio'
                      AND idgroup = '2ª jugada'
                      AND team = 'UD Atzeneta' THEN 1 END) as total_balls
        FROM MatchStats
        GROUP BY match, fecha, match_type, match_number
    )
    SELECT 
        match,
        fecha,
        match_number,
        won_balls,
        lost_balls,
        total_balls,
        ROUND((won_balls * 100.0) / NULLIF(total_balls, 0), 2) as blp_percentage
    FROM BallPossession
    ORDER BY fecha ASC;
    """
    return execute_query(query)