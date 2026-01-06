from django.urls import path
from .views import ExamListView, SubmitExamView,  SubmissionListView, SubmissionDetailView

urlpatterns = [
    path("exams/", ExamListView.as_view()),
    path("exams/<int:exam_id>/submit/", SubmitExamView.as_view()),
    path("submissions/", SubmissionListView.as_view()),
    path("submissions/<int:id>/", SubmissionDetailView.as_view()),
]
