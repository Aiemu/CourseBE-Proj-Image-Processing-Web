from django.db import models

# Create your models here.


class Record(models.Model):
    upload = models.ImageField(upload_to='1')
    dispose = models.ImageField(upload_to='2')
    time = models.DateField(auto_now_add=True)
    username = models.CharField(max_length=32)

