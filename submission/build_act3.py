"""Generate the filled-out Activity No. 3 answer sheet (DOCX).

Run with: .venv\\Scripts\\python.exe submission\\build_act3.py
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
GREEN = RGBColor(0x06, 0x3A, 0x25)
DARK = RGBColor(0x12, 0x25, 0x1B)
GOLD = RGBColor(0xB5, 0x8A, 0x10)


def shade(cell, color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def set_cell(cell, text, bold=False, color=None, size=9.5):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.font.name = "Calibri"
    if color:
        run.font.color.rgb = color


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, h in enumerate(headers):
        set_cell(table.rows[0].cells[i], h, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF), size=9.5)
        shade(table.rows[0].cells[i], "063A25")
    for r in rows:
        cells = table.add_row().cells
        for i, value in enumerate(r):
            set_cell(cells[i], str(value), size=9.5)
    if widths:
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Inches(w)
    doc.add_paragraph()
    return table


def para(doc, text, bold=False, italic=False, size=10.5, color=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    return p


def numbered(doc, n, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.first_line_indent = Inches(-0.3)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(f"{n}. ")
    run.bold = True
    run.font.color.rgb = GOLD
    body = p.add_run(text)
    body.font.size = Pt(10.5)


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.size = Pt(10.5)


def heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12.5)
    run.font.color.rgb = GREEN
    return p


def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(10.5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Republic of the Philippines\nCAVITE STATE UNIVERSITY\nCvSU Bacoor City Campus")
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = GREEN

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ACTIVITY NO. 3\n“From Blueprint to Working System” – SDLC Stage 3: Development")
    r.bold = True
    r.font.size = Pt(14)
    r.font.color.rgb = GREEN

    add_table(
        doc,
        ["NAME", "________________________________________", "SCORE", "____________"],
        [["SECTION", "________________________________________", "DATE", "____________"]],
        widths=[1.0, 3.3, 0.8, 1.7],
    )

    heading(doc, "GROUP MEMBERS (6 MEMBERS)")
    add_table(
        doc,
        ["No.", "Member Name", "Assigned Role"],
        [
            ["1", "________________________________", "Team Coordinator / Integration Lead"],
            ["2", "________________________________", "User Interface Developer"],
            ["3", "________________________________", "Core Function Developer (Application)"],
            ["4", "________________________________", "Core Function Developer (Enrollment)"],
            ["5", "________________________________", "Data / Database Developer"],
            ["6", "________________________________", "Validation / Documentation Lead"],
        ],
        widths=[0.5, 2.7, 3.6],
    )
    para(
        doc,
        "Note: Fill in the six names and the NAME / SECTION / DATE blanks above before submission.",
        italic=True,
        size=9.5,
        color=RGBColor(0x64, 0x76, 0x6B),
    )

    heading(doc, "Part 1: Review the Approved Design")
    numbered(
        doc,
        1,
        "System Name: CvSU Bacoor Online Enrollment System — a web-based admission and enrollment portal for Cavite State University, Bacoor City Campus.",
    )
    numbered(
        doc,
        2,
        "Problem the system addresses: Admission and enrollment were handled with paper forms and on-site queues. Students could not check application or enrollment status online, section selection and unit loading were manual, and the registrar had no single place to review applications, confirm enrollments, or monitor seat availability. The results were long lines, repeated campus visits, delayed or misplaced records, and poor visibility of who was admitted or enrolled for a term.",
    )
    numbered(
        doc,
        3,
        "Target users: (a) incoming applicants and students; (b) currently enrolled students; (c) registrar/administrative staff; and (d) the system administrator who maintains programs, terms, subjects and sections.",
    )
    numbered(
        doc,
        4,
        "Main functions/modules from Activity No. 2: a. Account registration and role-based login; b. Admission application submission and status tracking; c. Online enrollment with section selection and unit/seat validation; d. Registrar application review and enrollment confirmation; e. Subject offerings and seat monitoring; f. Administration of terms, programs, subjects and sections; g. Dashboards with status feedback.",
    )
    numbered(
        doc,
        5,
        "How the prototype follows the design: The approved wireframes became working Django templates — public landing, sign in/register, role-based dashboard, application form/status/detail, enrollment form/status, subject offerings, registrar dashboard, application review and enrollment management. The Activity 2 data entities were implemented as Django models (User, StudentProfile, Term, Program, Application, Subject, Section, Enrollment, EnrollmentSubject) with relationships and constraints. The process flow is enforced in code: register → apply → registrar review → approval → select sections (maximum 24 units, no full section, no duplicate section) → submit enrollment → registrar confirmation. Every status change is stored in the database and shown to both roles.",
    )

    heading(doc, "Part 2: Development Tools")
    numbered(doc, 1, "Programming language / platform: Python 3.12 with Django 5.2 on Windows; HTML5, CSS3 and JavaScript for the front end.")
    numbered(
        doc,
        2,
        "Frameworks or libraries: Django (MVT pattern, ORM, authentication, admin, forms and messages), django-environ for environment configuration, WhiteNoise for static files, Google Fonts (Poppins), and custom CSS/SVG assets for CvSU branding.",
    )
    numbered(
        doc,
        3,
        "Data storage / database: PostgreSQL through the DATABASE_URL setting for deployment, with a local SQLite database (db.sqlite3) as a fallback for the classroom demo. All data access uses the Django ORM; fictional sample records are loaded with `python manage.py seed_demo`.",
    )
    numbered(
        doc,
        4,
        "Why these tools: Python and Django allow rapid development of a secure, database-driven website with built-in login, admin and validation, which fits a six-member student team. The ORM lets the same code run on SQLite locally and PostgreSQL in deployment. The tools are free and open-source, and the custom CSS follows the CvSU Bacoor visual identity instead of a generic template.",
    )

    heading(doc, "Part 3: Build the Working Prototype")
    para(
        doc,
        "A working prototype was built with connected, database-backed screens and real interactions:",
        bold=True,
    )
    bullet(
        doc,
        "Screens: public landing page, sign in / register, student dashboard, application form, application status and detail, enrollment form, enrollment status, subject offerings, registrar dashboard, manage applications, review application, manage enrollments, and Django admin.",
    )
    bullet(
        doc,
        "Core function 1 — Accounts: email-based registration creates STUDENT users; login routes students and registrars to role-specific dashboards; access decorators block unauthorized pages.",
    )
    bullet(
        doc,
        "Core function 2 — Admission: students submit an application (program, year level, previous school, general average, personal statement), edit it while pending, and see the registrar's decision and remarks on their status page.",
    )
    bullet(
        doc,
        "Core function 3 — Enrollment: approved students choose sections, with validation for the 24-unit limit, section capacity, duplicate sections and one enrollment per term; a reference code is generated and the registrar confirms or drops the enrollment.",
    )
    bullet(
        doc,
        "Core function 4 — Registrar workflow: filter tabs, review forms, status dropdowns and dashboards read and update live database records.",
    )
    bullet(
        doc,
        "Navigation and controls work: top utility bar, role-based sidebar, filter tabs, forms, buttons and links. Invalid input shows field errors; successful actions show success messages; blocked actions show clear notices.",
    )
    bullet(
        doc,
        "Sample data only: three demo accounts, nine degree programs, fictional students and sections are generated by `seed_demo`. No real passwords, personal information or confidential records are used.",
    )

    heading(doc, "Part 4: Function Implementation Record")
    add_table(
        doc,
        ["Function / Module", "Assigned Member(s)", "Implementation / How It Works", "Status"],
        [
            [
                "Accounts & role-based access",
                "Member 1",
                "Custom email-based User model with STUDENT/ADMIN roles; registration, login/logout, role routing and permission decorators.",
                "Working",
            ],
            [
                "Public site & authentication UI",
                "Member 2",
                "CvSU-branded landing page, sign-in and registration screens, SVG seal/illustration, responsive green-and-gold CSS.",
                "Working",
            ],
            [
                "Admission application",
                "Member 3",
                "Application form with validation, status/detail pages, editable while pending, decision and remarks shown to the student.",
                "Working",
            ],
            [
                "Enrollment & registrar decisions",
                "Member 4",
                "Section selection with unit cap, seat and duplicate checks; generated reference code; registrar sets PENDING/ENROLLED/DROPPED/COMPLETED.",
                "Working",
            ],
            [
                "Data models & sample data",
                "Member 5",
                "Nine related models with migrations and unique constraints; Django admin registration; `seed_demo`; PostgreSQL/SQLite configuration.",
                "Working",
            ],
            [
                "Validation & documentation",
                "Member 6",
                "19 automated tests, browser verification of all screens, layout/cache fixes, README and this activity document with screenshots.",
                "Working",
            ],
        ],
        widths=[1.5, 1.0, 3.7, 0.9],
    )

    heading(doc, "Part 5: Data Implementation")
    numbered(
        doc,
        1,
        "Data stored or processed: accounts (email, full name, role, student number), student profiles, terms, degree programs, admission applications (type, previous school, general average, statement, status, remarks, timestamps and reviewer), subjects, sections (schedule, room, instructor, capacity), enrollments (reference code and status), and each enrollment's selected subjects.",
    )
    numbered(
        doc,
        2,
        "Where stored: PostgreSQL when DATABASE_URL is configured; otherwise the local SQLite file `db.sqlite3`. All records are created, read, updated and deleted through Django models and the ORM. Fictional sample records are loaded with `python manage.py seed_demo`.",
    )
    numbered(
        doc,
        3,
        "How information is handled: accounts are added through registration; applications through the application form; enrollments and selected sections through the enrollment form. Students view their own records on dashboards and status pages; the registrar updates application decisions and enrollment statuses through review/manage forms. Django admin manages terms, programs, subjects and sections. Unique constraints prevent duplicate applications, duplicate enrollments per term, and duplicate section selection.",
    )

    heading(doc, "Part 6: Individual Contribution Log")
    add_table(
        doc,
        ["Member Name", "Assigned Role", "Specific Work Completed", "Evidence / File / Feature"],
        [
            [
                "________________",
                "Team Coordinator / Integration Lead",
                "Organized tasks, integrated the accounts and enrollment apps, URLs, navigation and dashboards, and prepared the final demonstration.",
                "config/urls.py; templates/base.html; README.md",
            ],
            [
                "________________",
                "User Interface Developer",
                "Built the public landing page, sign-in and registration screens, CvSU seal and campus artwork, and responsive green/gold styling.",
                "templates/public/landing.html; static/css/landing.css; static/img/*.svg",
            ],
            [
                "________________",
                "Core Function Developer",
                "Implemented the admission application form, validation, application status/detail pages and the student dashboard.",
                "enrollment/views.py (apply, application_status); templates/enrollment/apply.html",
            ],
            [
                "________________",
                "Core Function Developer",
                "Implemented enrollment, section-selection rules, enrollment status, registrar review and status updates.",
                "enrollment/views.py (enroll, manage_*); enrollment/models.py",
            ],
            [
                "________________",
                "Data / Database Developer",
                "Designed models and migrations, seeded nine programs and demo users, and configured PostgreSQL with a SQLite fallback.",
                "accounts/models.py; enrollment/models.py; seed_demo.py; config/settings.py",
            ],
            [
                "________________",
                "Validation / Documentation Lead",
                "Wrote and ran 19 tests, checked every screen in a browser, fixed layout issues, prepared screenshots and this activity sheet.",
                "enrollment/tests.py; accounts/tests.py; submission/screenshots/; ACT-3-Answers.docx",
            ],
        ],
        widths=[1.1, 1.4, 2.7, 1.9],
    )

    heading(doc, "Part 7: Demonstration and Reflection")
    numbered(
        doc,
        1,
        "Three main functions to demonstrate: a. Student registration and role-based login; b. Submitting an admission application and viewing the registrar's decision; c. Selecting sections, passing the unit/seat validation, submitting an enrollment, and having the registrar confirm it.",
    )
    numbered(
        doc,
        2,
        "One development problem: keeping enrollment rules and statuses consistent for both students and registrars. We solved it by centralizing status choices in the models, validating unit load, seat capacity and duplicate sections in the view, adding database unique constraints, and covering the flow with automated tests.",
    )
    numbered(
        doc,
        3,
        "Incomplete features: automated email/SMS notifications and payment or fees integration are not implemented. The public News, Campuses and eLearning links point to the official CvSU website and are not locally managed content. These would require notification services, a payment gateway and a content-management feature before production use.",
    )
    numbered(
        doc,
        4,
        "Differences from the Activity 2 design: a public landing page was added for anonymous visitors; dashboards now show live counters and term details; navigation is role-based; a seed command and Django admin were added for setup; some wireframe screens were combined into status pages; and the visual design was refined with CvSU Bacoor branding, icons and illustrations.",
    )

    heading(doc, "Demo Credentials and Submission Contents")
    bullet(doc, "Admin: admin@example.com / Admin12345!")
    bullet(doc, "Student (pending application): student@example.com / Student12345!")
    bullet(doc, "Student (approved, pending enrollment): juan@example.com / Student12345!")
    bullet(
        doc,
        "Included with this sheet: the Django project source, a working prototype (run `start.bat` or `python manage.py runserver`), screenshots in `submission/screenshots/`, and automated tests (`python manage.py test`).",
    )

    heading(doc, "Appendix A — Screenshots of Implemented Functions")
    screenshots = [
        ("01-public-homepage.jpeg", "Figure 1. Public CvSU Bacoor landing page for anonymous visitors."),
        ("02-login.jpeg", "Figure 2. Role-based sign-in page with demo credentials."),
        ("03-student-dashboard.jpeg", "Figure 3. Student dashboard with application and enrollment status."),
        ("04-online-enrollment.jpeg", "Figure 4. Online enrollment with section selection, seats and unit summary."),
        ("05-registrar-dashboard.jpeg", "Figure 5. Registrar dashboard with live counters and recent applications."),
        ("06-review-application.jpeg", "Figure 6. Registrar application review with decision and remarks."),
    ]
    for name, caption in screenshots:
        path = ROOT / "screenshots" / name
        if path.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(path), width=Inches(6.3))
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cr = cp.add_run(caption)
            cr.italic = True
            cr.font.size = Pt(9)
            cp.paragraph_format.space_after = Pt(12)

    out = ROOT / "ACT-3-Answers.docx"
    doc.save(out)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
