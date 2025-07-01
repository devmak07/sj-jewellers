from django.db import models

# Create your models here.
class Merchant(models.Model):
    name=models.CharField(max_length=30,verbose_name='parcel name')
    touch=models.FloatField(verbose_name='Parcel Touch')
    Netwet=models.FloatField(verbose_name='net weight')
    Gowet=models.FloatField(verbose_name='Gross weight')
    PC=models.IntegerField(verbose_name='item PC')
    Item=models.TextField(max_length=100)

    def __str__(self):
        return str(self.id)