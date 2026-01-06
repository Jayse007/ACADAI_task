from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Exam, Submission, SubmissionAnswer
from .permission import IsOwnerOnly
from .serializers import (
    ExamSerializer,
    SubmissionCreateSerializer,
    SubmissionSerializer,
    SubmissionDetailSerializer
)
from .grading import grade_submission
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

class ExamListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exams = Exam.objects.all()
        return Response(ExamSerializer(exams, many=True).data)



class SubmitExamView(APIView):

    permission_classes = [IsAuthenticated]
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="exam_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID of the exam being submitted",
                required=True,
            )
        ],
        request=SubmissionCreateSerializer,
        responses={201: SubmissionSerializer},
    )

    @transaction.atomic  #This is used in order to avoid data corruption.
    def post(self, request, exam_id):
        exam = get_object_or_404(Exam, id=exam_id)

        serializer = SubmissionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        submission, created = Submission.objects.get_or_create(
            student=request.user,
            exam=exam,
        )

        if not created:
            return Response(
                {"detail": "Exam already submitted"},
                status=400,
            )

        answers = serializer.validated_data["answers"]

        questions = {
            str(q.id): q
            for q in exam.questions.all()
        }

        for qid, student_answer in answers.items():
            question = questions.get(qid)
            if not question:
                raise ValidationError(f"Invalid question ID {qid}")

            SubmissionAnswer.objects.create(
                submission=submission,
                question=question,
                student_answer=student_answer,
            )

        grade_submission(submission)

        return Response(
            SubmissionSerializer(submission).data,
            status=201,
        )


class SubmissionListView(ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(student=self.request.user).select_related("exam")

class SubmissionDetailView(RetrieveAPIView):
    serializer_class = SubmissionDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOnly]
    queryset = Submission.objects.select_related("exam", "student").prefetch_related("answers")
    lookup_field = 'id'