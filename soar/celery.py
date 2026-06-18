# soar/celery.py
import os
from celery import Celery

# Indique à Celery d'utiliser les settings de ton projet Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soar.settings')

app = Celery('soar')

# Charge la config depuis settings.py (préfixe: CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-détecte les fichiers tasks.py dans toutes les apps (alerts, etc.)
app.autodiscover_tasks()