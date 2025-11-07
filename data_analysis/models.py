from django.db import models

class DatasetConfig(models.Model):
    name = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)
    delimiter = models.CharField(max_length=10, default=',')
    encoding = models.CharField(max_length=50, default='utf-8')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dataset_configs'