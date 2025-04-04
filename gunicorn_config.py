# Configuración básica para Gunicorn - Optimizada para entornos con recursos limitados

# Puerto en el que Gunicorn escuchará
bind = "0.0.0.0:10000"

# Solo un worker - más simple para entornos con memoria limitada
workers = 1

# Aumentar el timeout para dar más tiempo a la carga inicial
timeout = 300

# Worker sincrónico básico
worker_class = "sync"

# Reducir threads para minimizar consumo de memoria
threads = 1

# Desactivar precarga para reducir consumo de memoria inicial
preload_app = False

# Nivel de log para mejor diagnóstico
loglevel = "debug"

# Deshabilitar max_requests para evitar reinicios
max_requests = 0
max_requests_jitter = 0

# Configuraciones de rendimiento para entornos limitados
worker_tmp_dir = "/dev/shm"
keepalive = 2

# Aumentar buffer para mejorar el manejo de conexiones
forwarded_allow_ips = '*'