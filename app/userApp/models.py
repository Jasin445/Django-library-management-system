from django.db import models


# Create your models here.
class Book(models.Model):
    title=models.CharField(100)
    author=models.CharField(60, null=False)
    isbn=models.BigIntegerField(unique=True)
    description=models.CharField(null=True, max_length=500)
    published_date=models.DateField(null=True)
    available=models.BooleanField(default=True)