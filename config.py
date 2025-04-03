"""
Configuración global de la aplicación UD Atzeneta Analytics
"""

# Configuración de la aplicación
APP_NAME = "UD Atzeneta Analytics"
SECRET_KEY = "ud_atzeneta_analytics_secret_key_2023_2024"

# Credenciales de usuario para la demo
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'dbeastbengal2324.cfo6g0og0ypz.eu-north-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'Villafranca.06',
    'database': 'UDAtzeneta',
    'charset': 'utf8mb4',
    'port': 3306
}

# Configuración de la interfaz
AUTO_REFRESH_INTERVAL = 30000  # 30 segundos para actualización automática

# Opciones de depuración
DEBUG = True          # Modo de depuración
USE_DUMMY_DATA = True # Usar datos simulados si no hay conexión a BD