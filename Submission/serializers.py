from rest_framework import serializers
from Exam.models import Exam
from Submission.models import Submission, SubmissionAnswer
from drf_spectacular.utils import extend_schema_field

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class SubmissionCreateSerializer(serializers.Serializer):
    answers = serializers.DictField(
        child=serializers.CharField(),
        help_text="Mapping of question_id to student_answer",
    )


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["id", "exam", "score", "submitted_at"]





class SubmissionAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source="question.text", read_only=True)

    class Meta:
        model = SubmissionAnswer
        fields = ["question", "question_text", "student_answer", "awarded_score"]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    answers = SubmissionAnswerSerializer(many=True, read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)

    class Meta:
        model = Submission
        fields = ["id", "exam", "exam_title", "score", "submitted_at", "answers"]
