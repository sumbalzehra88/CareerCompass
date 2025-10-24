from django.db import models

# Create your models here.

class Internships(models.Model):
    internship_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    title = models.CharField(max_length=255)
    duration = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    skills_required = models.CharField(max_length=255)
    deadline = models.DateField()
    description = models.TextField()

    def __str__(self):
        return self.title

