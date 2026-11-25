# Activity No. 3 — “From Blueprint to Working System” (SDLC Stage 3: Development)

**Name:** ____________________  **Section:** ____________  **Score:** __________

> Fill in the group members' names in the DOCX version before submission.

## Group Members (6 Members)

| No. | Member Name | Assigned Role |
| --- | --- | --- |
| 1 | ________________________ | Team Coordinator / Integration Lead |
| 2 | ________________________ | User Interface Developer |
| 3 | ________________________ | Core Function Developer (Application) |
| 4 | ________________________ | Core Function Developer (Enrollment) |
| 5 | ________________________ | Data / Database Developer |
| 6 | ________________________ | Validation / Documentation Lead |

## Part 1: Review the Approved Design

1. **System Name:** CvSU Bacoor Online Enrollment System — a web-based admission and enrollment portal for Cavite State University, Bacoor City Campus.
2. **Problem the system addresses:** Admission and enrollment were handled with paper forms and on-site queues. Students could not check application or enrollment status online, section selection and unit loading were manual, and the registrar had no single place to review applications, confirm enrollments, or monitor seat availability. The results were long lines, repeated campus visits, delayed or misplaced records, and poor visibility of who was admitted or enrolled for a term.
3. **Target users:** incoming applicants and students; currently enrolled students; registrar/administrative staff; and the system administrator who maintains programs, terms, subjects and sections.
4. **Main functions/modules:** (a) account registration and role-based login; (b) admission application submission and status tracking; (c) online enrollment with section selection and unit/seat validation; (d) registrar application review and enrollment confirmation; (e) subject offerings and seat monitoring; (f) administration of terms, programs, subjects and sections; (g) dashboards with status feedback.
5. **How the prototype follows the design:** The approved wireframes became working Django templates — public landing, sign in/register, role-based dashboard, application form/status/detail, enrollment form/status, subject offerings, registrar dashboard, application review and enrollment management. The Activity 2 data entities were implemented as Django models (User, StudentProfile, Term, Program, Application, Subject, Section, Enrollment, EnrollmentSubject) with relationships and constraints. The process flow is enforced in code: register → apply → registrar review → approval → select sections (maximum 24 units, no full section, no duplicate section) → submit enrollment → registrar confirmation. Every status change is stored in the database and shown to both roles.

## Part 2: Development Tools

1. **Programming language / platform:** Python 3.12 with Django 5.2 on Windows; HTML5, CSS3 and JavaScript for the front end.
2. **Frameworks or libraries:** Django (MVT pattern, ORM, authentication, admin, forms and messages), django-environ for environment configuration, WhiteNoise for static files, Google Fonts (Poppins), and custom CSS/SVG assets for CvSU branding.
3. **Data storage / database:** PostgreSQL through the `DATABASE_URL` setting for deployment, with a local SQLite database (`db.sqlite3`) as a fallback for the classroom demo. All data access uses the Django ORM; fictional sample records are loaded with `python manage.py seed_demo`.
4. **Why these tools:** Python and Django allow rapid development of a secure, database-driven website with built-in login, admin and validation, which fits a six-member student team. The ORM lets the same code run on SQLite locally and PostgreSQL in deployment. The tools are free and open-source, and the custom CSS follows the CvSU Bacoor visual identity instead of a generic template.

## Part 3: Build the Working Prototype

A working prototype was built with connected, database-backed screens and real interactions:

- **Screens:** public landing page, sign in / register, student dashboard, application form, application status and detail, enrollment form, enrollment status, subject offerings, registrar dashboard, manage applications, review application, manage enrollments, and Django admin.
- **Core function 1 — Accounts:** email-based registration creates STUDENT users; login routes students and registrars to role-specific dashboards; access decorators block unauthorized pages.
- **Core function 2 — Admission:** students submit an application (program, year level, previous school, general average, personal statement), edit it while pending, and see the registrar's decision and remarks on their status page.
- **Core function 3 — Enrollment:** approved students choose sections, with validation for the 24-unit limit, section capacity, duplicate sections and one enrollment per term; a reference code is generated and the registrar confirms or drops the enrollment.
- **Core function 4 — Registrar workflow:** filter tabs, review forms, status dropdowns and dashboards read and update live database records.
- **Navigation and controls work:** top utility bar, role-based sidebar, filter tabs, forms, buttons and links. Invalid input shows field errors; successful actions show success messages; blocked actions show clear notices.
- **Sample data only:** three demo accounts, nine degree programs, fictional students and sections are generated by `seed_demo`. No real passwords, personal information or confidential records are used.

## Part 4: Function Implementation Record

| Function / Module | Assigned Member(s) | Implementation / How It Works | Status |
| --- | --- | --- | --- |
| Accounts & role-based access | Member 1 | Custom email-based User model with STUDENT/ADMIN roles; registration, login/logout, role routing and permission decorators. | Working |
| Public site & authentication UI | Member 2 | CvSU-branded landing page, sign-in and registration screens, SVG seal/illustration, responsive green-and-gold CSS. | Working |
| Admission application | Member 3 | Application form with validation, status/detail pages, editable while pending, decision and remarks shown to the student. | Working |
| Enrollment & registrar decisions | Member 4 | Section selection with unit cap, seat and duplicate checks; generated reference code; registrar sets PENDING/ENROLLED/DROPPED/COMPLETED. | Working |
| Data models & sample data | Member 5 | Nine related models with migrations and unique constraints; Django admin registration; `seed_demo`; PostgreSQL/SQLite configuration. | Working |
| Validation & documentation | Member 6 | 19 automated tests, browser verification of all screens, layout/cache fixes, README and this activity document with screenshots. | Working |

## Part 5: Data Implementation

1. **Data stored or processed:** accounts (email, full name, role, student number), student profiles, terms, degree programs, admission applications (type, previous school, general average, statement, status, remarks, timestamps and reviewer), subjects, sections (schedule, room, instructor, capacity), enrollments (reference code and status), and each enrollment's selected subjects.
2. **Where stored:** PostgreSQL when `DATABASE_URL` is configured; otherwise the local SQLite file `db.sqlite3`. All records are created, read, updated and deleted through Django models and the ORM. Fictional sample records are loaded with `python manage.py seed_demo`.
3. **How information is handled:** accounts are added through registration; applications through the application form; enrollments and selected sections through the enrollment form. Students view their own records on dashboards and status pages; the registrar updates application decisions and enrollment statuses through review/manage forms. Django admin manages terms, programs, subjects and sections. Unique constraints prevent duplicate applications, duplicate enrollments per term, and duplicate section selection.

## Part 6: Individual Contribution Log

| Member Name | Assigned Role | Specific Work Completed | Evidence / File / Feature |
| --- | --- | --- | --- |
| ________________ | Team Coordinator / Integration Lead | Organized tasks, integrated the accounts and enrollment apps, URLs, navigation and dashboards, and prepared the final demonstration. | `config/urls.py`; `templates/base.html`; `README.md` |
| ________________ | User Interface Developer | Built the public landing page, sign-in and registration screens, CvSU seal and campus artwork, and responsive green/gold styling. | `templates/public/landing.html`; `static/css/landing.css`; `static/img/*.svg` |
| ________________ | Core Function Developer | Implemented the admission application form, validation, application status/detail pages and the student dashboard. | `enrollment/views.py` (apply, application_status); `templates/enrollment/apply.html` |
| ________________ | Core Function Developer | Implemented enrollment, section-selection rules, enrollment status, registrar review and status updates. | `enrollment/views.py` (enroll, manage_*); `enrollment/models.py` |
| ________________ | Data / Database Developer | Designed models and migrations, seeded nine programs and demo users, and configured PostgreSQL with a SQLite fallback. | `accounts/models.py`; `enrollment/models.py`; `seed_demo.py`; `config/settings.py` |
| ________________ | Validation / Documentation Lead | Wrote and ran 19 tests, checked every screen in a browser, fixed layout issues, prepared screenshots and this activity sheet. | `enrollment/tests.py`; `accounts/tests.py`; `submission/screenshots/`; `ACT-3-Answers.docx` |

## Part 7: Demonstration and Reflection

1. **Three main functions to demonstrate:** (a) student registration and role-based login; (b) submitting an admission application and viewing the registrar's decision; (c) selecting sections, passing the unit/seat validation, submitting an enrollment, and having the registrar confirm it.
2. **One development problem:** keeping enrollment rules and statuses consistent for both students and registrars. We solved it by centralizing status choices in the models, validating unit load, seat capacity and duplicate sections in the view, adding database unique constraints, and covering the flow with automated tests.
3. **Incomplete features:** automated email/SMS notifications and payment or fees integration are not implemented. The public News, Campuses and eLearning links point to the official CvSU website and are not locally managed content. These would require notification services, a payment gateway and a content-management feature before production use.
4. **Differences from the Activity 2 design:** a public landing page was added for anonymous visitors; dashboards now show live counters and term details; navigation is role-based; a seed command and Django admin were added for setup; some wireframe screens were combined into status pages; and the visual design was refined with CvSU Bacoor branding, icons and illustrations.

## Demo Credentials and Submission Contents

- Admin: `admin@example.com` / `Admin12345!`
- Student (pending application): `student@example.com` / `Student12345!`
- Student (approved, pending enrollment): `juan@example.com` / `Student12345!`
- Included: Django project source, working prototype (`start.bat` or `python manage.py runserver`), screenshots in `submission/screenshots/`, and automated tests (`python manage.py test`).

## Appendix A — Screenshots

1. `screenshots/01-public-homepage.jpeg` — Public CvSU Bacoor landing page.
2. `screenshots/02-login.jpeg` — Role-based sign-in page.
3. `screenshots/03-student-dashboard.jpeg` — Student dashboard with application/enrollment status.
4. `screenshots/04-online-enrollment.jpeg` — Section selection with seats and unit summary.
5. `screenshots/05-registrar-dashboard.jpeg` — Registrar dashboard with live counters.
6. `screenshots/06-review-application.jpeg` — Registrar review with decision and remarks.
