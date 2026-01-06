from django.db import models
from Exam.models import Exam
# Create your models here.



class Question(models.Model):
    QUESTION_TYPES = (
        ("mcq", "Multiple Choice"),
        ("obj", "Objective"),
        ("essay", "Essay"),
    )

    exam = models.ForeignKey(Exam, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    expected_answer = models.TextField()
    max_score = models.FloatField(default=1.0)

    class Meta:
        indexes = [
            models.Index(fields=["exam", "question_type"]),
        ]
