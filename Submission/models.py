from django.db import models
from django.contrib.auth.models import User
from Exam.models import Exam
from Question.models import Question


# Create your models here.
class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=["student", "exam"], name="student_to_exam_unique" #This also creates an index for student to exam
        )]
        

class SubmissionAnswer(models.Model):
    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student_answer = models.TextField(max_length=6000)
    awarded_score = models.FloatField(blank=True, null=True)



