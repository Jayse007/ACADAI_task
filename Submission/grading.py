from django.db import transaction
from .models import Submission


class BaseGrader:
    def grade(self, expected_answer, student_answer, max_score):
        raise NotImplementedError



class ObjectiveGrader(BaseGrader):
    """
    Handles:
    - Single correct answer
    - Numeric ranges (e.g. "10-20")
    """
    def grade(self, expected_answer, student_answer, max_score):
        expected = expected_answer.strip().lower()
        student = str(student_answer).strip().lower()

        # Numeric range support
        if "-" in expected:
            try:
                start, end = map(float, expected.split("-"))
                value = float(student)
                return max_score if start <= value <= end else 0.0
            except ValueError:
                return 0.0

        # Exact match
        return max_score if student == expected else 0.0



class EssayGrader(BaseGrader):
    """
    Keyword-based partial credit grader.
    expected_answer = "keyword1, keyword2, keyword3"
    """
    def grade(self, expected_answer, student_answer, max_score):
        expected_keywords = [
            k.strip().lower()
            for k in expected_answer.split(",")
            if k.strip()
        ]

        student_text = str(student_answer).lower()

        if not expected_keywords:
            return 0.0

        matched = sum(
            1 for kw in expected_keywords if kw in student_text
        )

        score = (matched / len(expected_keywords)) * max_score
        return round(score, 2)


# -----------------------------
# Grade Submission
# -----------------------------
def grade_submission(submission: Submission):
    """
    Grades all answers in a submission.

    Guarantees:
    - Objective questions never use TF-IDF
    - Essay questions get partial credit
    - Atomic update of answers + submission score
    """
    total_score = 0.0

    with transaction.atomic():
        answers = submission.answers.select_related("question")

        for ans in answers:
            question = ans.question

            if question.question_type == "essay":
                grader = EssayGrader()
            else:
                grader = ObjectiveGrader()

            score = grader.grade(
                expected_answer=question.expected_answer,
                student_answer=ans.student_answer,
                max_score=question.max_score,
            )

            ans.awarded_score = score
            ans.save()
            total_score += score

        submission.score = round(total_score, 2)
        submission.save()

    return submission.score
