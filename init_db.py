import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from data_analysis.models import DatasetConfig

# Crear configuración inicial
DatasetConfig.objects.create(
    name='Bookings Dataset',
    file_path='data/bookings.csv',
    delimiter=',',
    encoding='utf-8',
    active=True
)

print("Base de datos inicializada correctamente!")