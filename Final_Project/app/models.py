from django.db import models

# Create your models here.


class Record(models.Model):
    upload = models.ImageField(upload_to='1')
    seg = models.CharField(max_length=128)
    det = models.CharField(max_length=128)
    sty = models.CharField(max_length=128)
    operation = models.CharField(max_length=32)
    time = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=32)

