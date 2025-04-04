# Configuración básica para Gunicorn

# Puerto en el que Gunicorn escuchará
bind = "0.0.0.0:10000"

# Número de workers (procesos) que Gunicorn lanzará
# Para planes gratuitos de Render con recursos limitados, menos workers pueden ser más eficientes
workers = 2

# Timeout en segundos
timeout = 120

# Clase de worker a utilizar
worker_class = "gevent"

# Nivel de log
loglevel = "info"

# Permite a Gunicorn recargar automáticamente cuando detecta cambios en el código
reload = True