# Acad AI – Mini Assessment Engine

## Overview (What this app is)

Acad AI is a **web-based assessment system** that allows:

* Students to **register and log in**
* Students to **take exams**
* Students to **submit answers securely**
* The system to **automatically grade submissions**
* Administrators or reviewers to **inspect results**
* Frontend teams to **integrate easily using documented APIs**

This project demonstrates how Acad AI’s core assessment logic works behind the scenes.

---

## What You Can Access (User Interface)

This project exposes a **browser-based interface** for interacting with the system.
You **do not need programming knowledge** to use it.

### 1. Interactive API UI (Recommended)

This is the **main interface** you should use.

```
http://localhost:8000/docs/
```

What this page allows you to do:

* View all available features (endpoints)
* Register users
* Log in
* Submit exams
* View submissions
* Test the system end-to-end
* Authenticate securely with one click

Think of this page as the **control panel** of the application.

---

## How to Start the App (One-Time Setup)

A developer will normally do this step, but it helps to understand the flow.

From the project folder, run:

```
python manage.py runserver
```

Once started, the app runs at:

```
http://localhost:8000/
```

---

## Key Pages and URLs (Important)

### API Documentation (Main UI)

```
/docs/
```

* Human-friendly interface
* Click buttons instead of writing code
* Best place to explore features

---

### API Schema (Technical, optional)

```
/schema/
```

* Machine-readable documentation
* Used by frontend and mobile apps
* Not required for normal use

---

## Authentication (Login & Registration)

Before using most features, a user must be logged in.

### Register a New User

```
POST /api/auth/register/
```

What it does:

* Creates a new user account
* Returns a login token automatically

You can do this visually inside `/docs/`.

---

### Login

```
POST /api/auth/login/
```

What it does:

* Logs an existing user in
* Returns an authentication token

---

### How Login Works in the UI

1. Go to `/docs/`
2. Use **Register** or **Login**
3. Copy the returned token
4. Click **Authorize** (top right)
5. Paste:

   ```
   Bearer YOUR_TOKEN_HERE
   ```
6. You are now logged in

Once authorized, all locked features become accessible.

---

## Exams & Submissions (Core Functionality)

### Submit an Exam

```
POST /api/exams/{exam_id}/submit/
```

What happens:

* Student submits answers
* System validates submission
* System automatically grades answers
* Score is saved securely
* Duplicate submissions are blocked

---

### View Submissions

```
GET /api/submissions/
```

Shows:

* Exams taken
* Scores
* Submission timestamps

---

### View a Single Submission

```
GET /api/submissions/{id}/
```

Shows:

* Detailed answers
* Score breakdown
* Exam reference

---

## Automated Grading (How scoring works)

The grading system is **automatic and immediate**.

Depending on the question type:

* Objective answers → exact or numeric match
* Written answers → keyword similarity
* Essay answers → partial credit based on relevance

The grading logic is **modular**, meaning:

* It can be upgraded later
* External AI graders can be plugged in
* Scores are transparent and auditable

---

## Data Safety & Security

The system enforces:

* Secure authentication
* Students can only see **their own submissions**
* No duplicate exam submissions
* Database-level consistency (no partial saves)
* Atomic transactions to prevent corruption

This matches **production-grade backend standards**.

---

## Testing (Quality Assurance)

The project includes **automated tests** to ensure correctness.

### What is tested?

* User registration & login
* Authentication enforcement
* Exam submission flow
* Duplicate submission blocking
* Grading accuracy
* Database safety (atomic transactions)
* Error handling

### How tests are run

```
python manage.py test
```

Tests automatically:

* Create a temporary database
* Simulate real users
* Validate scoring logic
* Ensure nothing breaks silently

No real data is affected.

---

## Who This Is For

* Employers reviewing backend quality
* Frontend developers integrating APIs
* Product managers validating logic
* QA teams verifying correctness

---

## Summary (In Plain Terms)

* This app is a **secure online exam system**
* You interact with it through a **web-based UI**
* No coding knowledge is required to test features
* All important actions are visible and documented
* The system is reliable, tested, and extensible

---

