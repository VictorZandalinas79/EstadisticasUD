# gunicorn_config.py
import os

bind = f"0.0.0.0:{int(os.environ.get('PORT', 10000))}"
workers = 4  # número de workers
timeout = 120  # timeout en segundos
worker_class = 'sync'