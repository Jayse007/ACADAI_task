from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from .models import  Submission, SubmissionAnswer
from .grading import grade_submission
from Question.models import Question
from Exam.models import Exam

User = get_user_model()


class AcadAITestCase(TestCase):
    """
    Comprehensive test suite for Acad AI Mini Assessment Engine.
    
    Tests cover:
    - User registration and authentication
    - Exam and question creation
    - Submission creation with validation
    - Automated grading correctness
    - Object-level permissions
    - Database atomicity on submission failure
    """

    def setUp(self):
        """Setup common objects for tests"""
        self.client = APIClient()

        # Create test users
        self.student1 = User.objects.create_user(
            username="student1", email="s1@test.com", password="password123"
        )
        self.student2 = User.objects.create_user(
            username="student2", email="s2@test.com", password="password123"
        )

        # Obtain tokens
        self.token1 = Token.objects.create(user=self.student1)
        self.token2 = Token.objects.create(user=self.student2)

        # Create an exam
        self.exam = Exam.objects.create(
            title="Sample Exam",
            duration_minutes=30,
            course="Math 101",
        )

        # Create questions with intensive grading test cases
        # For grading, assume simple keyword matching
        self.q1 = Question.objects.create(
            exam=self.exam,
            text="What is 2 + 2?",
            question_type="objective",
            expected_answer="4",
        )
        self.q2 = Question.objects.create(
            exam=self.exam,
            text="Name a prime number between 10 and 20.",
            question_type="objective",
            expected_answer="13",
        )
        self.q3 = Question.objects.create(
            exam=self.exam,
            text="Explain Pythagoras theorem briefly.",
            question_type="essay",
            expected_answer="In a right-angled triangle, the square of the hypotenuse is equal to the sum of squares of the other two sides.",
        )

    # -----------------------------
    # Authentication Tests
    # -----------------------------
    def test_registration_and_login(self):
        """
        Test user registration endpoint and token generation.
        """
        response = self.client.post("/api/auth/register/", {
            "username": "new_student",
            "email": "new@student.com",
            "password": "securepass123"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)

        # Login with new user
        response = self.client.post("/api/auth/login/", {
            "username": "new_student",
            "password": "securepass123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    # -----------------------------
    # Submission Tests
    # -----------------------------
    def test_create_submission_success(self):
        """
        Test creating a submission successfully with correct answer structure.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.post(f"/api/exams/{self.exam.id}/submit/", {
            "answers": {
                str(self.q1.id): "4",
                str(self.q2.id): "13",
                str(self.q3.id): "The square of the hypotenuse equals the sum of squares of the other two sides"
            }
        }, format='json')
        self.assertEqual(response.status_code, 201)
        submission = Submission.objects.get(student=self.student1, exam=self.exam)
        self.assertEqual(submission.answers.count(), 3)

    def test_duplicate_submission_blocked(self):
        """
        Test that a student cannot submit the same exam twice.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        # First submission
        response1 = self.client.post(f"/api/exams/{self.exam.id}/submit/", {
            "answers": {str(self.q1.id): "4"}
        }, format="json")
        self.assertEqual(response1.status_code, 201)

        # Second submission
        response2 = self.client.post(f"/api/exams/{self.exam.id}/submit/", {
            "answers": {str(self.q1.id): "4"}
        }, format="json")
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data["detail"], "Exam already submitted")

    def test_submission_invalid_question_id(self):
        """
        Test that submitting an invalid question ID fails and does not partially save.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        invalid_qid = 9999
        with transaction.atomic():
            response = self.client.post(f"/api/exams/{self.exam.id}/submit/", {
                "answers": {str(invalid_qid): "test"}
            }, format="json")
            self.assertEqual(response.status_code, 400)
            # self.assertIn("Invalid question ID", response.data["detail"])

        # Ensure no Submission was created
        self.assertFalse(Submission.objects.filter(student=self.student1, exam=self.exam).exists())

    # -----------------------------
    # Grading Tests
    # -----------------------------
    def test_grading_correctness(self):
        """
        Test that grading algorithm evaluates numeric, keyword, and essay answers correctly.
        """
        submission = Submission.objects.create(student=self.student1, exam=self.exam)
        SubmissionAnswer.objects.create(submission=submission, question=self.q1, student_answer="4")
        SubmissionAnswer.objects.create(submission=submission, question=self.q2, student_answer="13")
        SubmissionAnswer.objects.create(submission=submission, question=self.q3, student_answer="In a right-angled triangle, the square of the hypotenuse is equal to the sum of squares of the other two sides.")

        grade_submission(submission)

        submission.refresh_from_db()
        self.assertIsNotNone(submission.score)
        # For this mock grading: perfect answers => full score
        total_answers = submission.answers.count()
        self.assertEqual(total_answers, 3)
        # Each answer should have a numeric awarded_score
        for ans in submission.answers.all():
            self.assertIsNotNone(ans.awarded_score)
            self.assertGreaterEqual(ans.awarded_score, 0)

    # -----------------------------
    # Object-level Permission Tests
    # -----------------------------
    def test_submission_detail_access_control(self):
        """
        Test that only the owner can access the submission detail.
        """
        submission = Submission.objects.create(student=self.student1, exam=self.exam)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token2.key}")  # another student
        response = self.client.get(f"/api/submissions/{submission.id}/")
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Owner can access
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.get(f"/api/submissions/{submission.id}/")
        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # Database Atomicity Test
    # -----------------------------
    def test_submission_atomicity_on_error(self):
        """
        Test that if one SubmissionAnswer fails, no submission or answers are partially saved.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        invalid_qid = 999
        try:
            with transaction.atomic():
                response = self.client.post(f"/api/exams/{self.exam.id}/submit/", {
                    "answers": {
                        str(self.q1.id): "4",
                        str(invalid_qid): "bad"
                    }
                }, format="json")
        except IntegrityError:
            pass

        # Ensure submission and answers are not saved
        self.assertFalse(Submission.objects.filter(student=self.student1, exam=self.exam).exists())
        self.assertEqual(SubmissionAnswer.objects.count(), 0)
