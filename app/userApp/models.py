import uuid

from django.db import models


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=17, unique=True)
    description = models.TextField(null=True)
    published_date = models.DateField(null=True)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Student(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4)
    first_name=models.CharField(max_length=150)
    last_name=models.CharField(max_length=150)
    level=models.IntegerField()
    department=models.CharField(max_length=200)

class LibraryRecord(models.Model):
    book=models.ForeignKey(Book, on_delete=models.CASCADE)
    student=models.ForeignKey(Student, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at=models.DateTimeField()
    returned_at=models.DateTimeField(null=True, blank=True)