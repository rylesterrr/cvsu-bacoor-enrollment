# CvSU Bacoor Online Enrollment System

A Django web application for Cavite State University – Bacoor City Campus. It lets students apply for admission, track application and enrollment status, choose sections online, and gives the registrar tools to review applications and confirm enrollments.

## Quick start (Windows)

1. Double-click `start.bat`. It creates a project-local virtual environment if needed, opens the browser, and starts the server.
2. Or run manually:

   ```bat
   py -m venv .venv
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   .venv\Scripts\python.exe manage.py migrate
   .venv\Scripts\python.exe manage.py seed_demo
   .venv\Scripts\python.exe manage.py runserver
   ```

3. Visit `http://127.0.0.1:8000/`.

## Demo accounts

| Role | Email | Password | Notes |
| --- | --- | --- | --- |
| Admin / Registrar | `admin@example.com` | `Admin12345!` | Reviews applications, confirms enrollments |
| Student | `student@example.com` | `Student12345!` | Pending application |
| Student | `juan@example.com` | `Student12345!` | Approved application, pending enrollment |

All data is fictional. `seed_demo` can be re-run to reset the sample records.

## Main URLs

- `/` — public CvSU Bacoor landing page (authenticated users go to the dashboard)
- `/accounts/login/`, `/accounts/register/` — authentication
- `/dashboard/` — role-based dashboard
- `/apply/`, `/application/`, `/enroll/`, `/enrollment/`, `/subjects/` — student portal
- `/manage/applications/`, `/manage/enrollments/` — registrar portal
- `/admin/` — Django administration

## Technology

- Python 3.12, Django 5.2, HTML/CSS/JavaScript
- PostgreSQL via `DATABASE_URL`; SQLite (`db.sqlite3`) fallback for local demo
- django-environ, WhiteNoise, Google Fonts (Poppins)
- Custom CvSU-branded CSS and SVG assets

## Tests

```bat
.venv\Scripts\python.exe manage.py test
```

19 automated tests cover authentication, application and enrollment workflows, validation rules, registrar actions, the seed command, and the public landing page.

## Publish online (Render)

`render.yaml` is included, so deployment takes only a few steps:

1. Create a free account at https://render.com and connect your GitHub account.
2. Push this project to a GitHub repository (see "Push to GitHub" below).
3. In Render, choose **New + → Blueprint** and select that repository.
4. Name the blueprint anything you like and keep the default service name
   `cvsu-bacoor-enrollment` (or edit `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` in `render.yaml`
   if you rename it — the app also detects Render's hostname automatically).
5. Click **Apply**. Render creates the PostgreSQL database and web service, installs
   dependencies, collects static files, runs migrations and seeds the demo accounts.
6. Open the URL shown on the service page (for example
   `https://cvsu-bacoor-enrollment.onrender.com`). First load may take a few seconds on the free plan.

Log in with the demo accounts listed above. To use real accounts later, change the seeded
passwords in the Django admin or run `manage.py changepassword <email>` from the Render Shell.

### Push to GitHub

If the folder is not a Git repository yet:

```bat
git init
git add .
git commit -m "CvSU Bacoor Online Enrollment System"
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

`.env`, `.venv/`, `db.sqlite3` and `staticfiles/` are already ignored, so secrets and local
data will not be uploaded. The deployment uses Render's environment variables instead.

## Activity No. 3 submission

- `submission/ACT-3-Answers.docx` — completed activity sheet with six screenshots
- `submission/ACT-3-Answers.md` — plain-text copy of the answers
- `submission/screenshots/` — screenshots of the implemented functions
- `submission/build_act3.py` — regenerates the DOCX from the screenshots and answers

Before submitting, fill in the group member names and NAME / SECTION / DATE fields in the DOCX.
