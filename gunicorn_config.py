# Configuración básica para Gunicorn

# Puerto en el que Gunicorn escuchará
bind = "0.0.0.0:10000"

# Número de workers (procesos) que Gunicorn lanzará
# Para planes gratuitos de Render con recursos limitados, menos workers pueden ser más eficientes
workers = 1

# Timeout en segundos
timeout = 120

# Clase de worker a utilizar - usado el worker sync que es más básico pero confiable
worker_class = "sync"

# Nivel de log
loglevel = "info"

# Threads por worker
threads = 2

# Tiempo de precarga
preload_app = True

# Opciones de worker
max_requests = 1000
max_requests_jitter = 50