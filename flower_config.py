# Flower Configuration for OrderFlow
# This file helps fix DataTables Ajax errors and improves monitoring stability

import os

# Broker and Result Backend
broker_url = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Flower Settings
port = 5555
address = '0.0.0.0'
url_prefix = ''
max_tasks = 10000
persistent = True
db = '/tmp/flower.db'
auto_refresh = True
auto_refresh_rate = 10.0

# Authentication
basic_auth = os.environ.get('FLOWER_BASIC_AUTH', 'admin:flower123')

# Task Settings
task_ignore_result = False
task_send_sent_event = True
worker_send_task_events = True

# API Settings
enable_events = True
enable_events_http = True

# Debug Settings
debug = False
logging = 'INFO'

# CORS Settings (for DataTables)
cors_origins = ['*']

# Timeout Settings
worker_timeout = 30
task_timeout = 30

# Refresh Settings
auto_refresh_rate = 10.0
