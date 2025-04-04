# Configuración óptima para Gunicorn con aplicaciones Dash en Render

# Puerto en el que Gunicorn escuchará
bind = "0.0.0.0:10000"

# Configuración de workers
workers = 1  # Usar un solo worker para el plan gratuito de Render
worker_class = "sync"  # Clase de worker más estable
threads = 2  # Hilos por worker

# Timeouts
timeout = 300  # Extender el timeout para la carga inicial
keepalive = 5  # Mantener conexiones vivas

# Optimizaciones para el rendimiento
worker_tmp_dir = "/dev/shm"  # Usar memoria compartida para archivos temporales
preload_app = False  # No precargar app para reducir uso de memoria al inicio

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Configuraciones de seguridad
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}

# Manejo de errores
capture_output = True  # Capturar salida estándar

# Configuración para evitar reinicios frecuentes
max_requests = 0  # Deshabilitar reinicio por número de solicitudes