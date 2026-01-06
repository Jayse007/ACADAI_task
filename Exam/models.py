from django.db import models


# Create your models here.
class Exam(models.Model):
    title = models.CharField(max_length=255)
    course = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField()
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["course"]),
        ]

