from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from enrollment.models import (
    Application,
    Enrollment,
    EnrollmentSubject,
    Program,
    Section,
    StudentProfile,
    Subject,
    Term,
)


class Command(BaseCommand):
    help = "Create demo programs, a term, sections, students, applications, and enrollments."

    @transaction.atomic
    def handle(self, *args, **options):
        admin = self._ensure_user(
            "admin@example.com", "Admin12345!", "Registrar Admin", User.Role.ADMIN
        )
        maria = self._ensure_user(
            "student@example.com", "Student12345!", "Maria Santos", User.Role.STUDENT
        )
        juan = self._ensure_user(
            "juan@example.com", "Student12345!", "Juan Dela Cruz", User.Role.STUDENT
        )

        bsit, _ = Program.objects.get_or_create(
            code="BSIT",
            defaults={
                "name": "Bachelor of Science in Information Technology",
                "description": "Software development, networking, and information systems.",
            },
        )
        bscs, _ = Program.objects.get_or_create(
            code="BSCS",
            defaults={
                "name": "Bachelor of Science in Computer Science",
                "description": "Algorithms, computing theory, and software engineering.",
            },
        )
        bsba, _ = Program.objects.get_or_create(
            code="BSBA",
            defaults={
                "name": "Bachelor of Science in Business Administration",
                "description": "Management, marketing, and business operations.",
            },
        )
        Program.objects.get_or_create(
            code="BSBA-MM",
            defaults={
                "name": "BSBA major in Marketing Management",
                "description": "Marketing strategy, consumer behavior, and brand management.",
            },
        )
        Program.objects.get_or_create(
            code="BSPSYCH",
            defaults={
                "name": "Bachelor of Science in Psychology",
                "description": "Human behavior, mental processes, and psychological research.",
            },
        )
        Program.objects.get_or_create(
            code="BSCRIM",
            defaults={
                "name": "Bachelor of Science in Criminology",
                "description": "Criminal justice, law enforcement, and public safety.",
            },
        )
        Program.objects.get_or_create(
            code="BSHM",
            defaults={
                "name": "Bachelor of Science in Hospitality Management",
                "description": "Tourism, hospitality operations, and service management.",
            },
        )
        Program.objects.get_or_create(
            code="BSEd-EN",
            defaults={
                "name": "BSEd major in English",
                "description": "Teaching English language and literature in secondary schools.",
            },
        )
        Program.objects.get_or_create(
            code="BSEd-MATH",
            defaults={
                "name": "BSEd major in Mathematics",
                "description": "Teaching mathematics in secondary schools.",
            },
        )

        today = timezone.localdate()
        term, _ = Term.objects.get_or_create(
            school_year="2026-2027",
            semester=Term.Semester.FIRST,
            defaults={
                "enrollment_open": True,
                "enrollment_deadline": today + timedelta(days=30),
                "classes_start": today + timedelta(days=45),
                "is_active": True,
            },
        )
        term.enrollment_open = True
        term.is_active = True
        term.enrollment_deadline = today + timedelta(days=30)
        term.classes_start = today + timedelta(days=45)
        term.save()
        Term.objects.exclude(pk=term.pk).update(is_active=False)

        subject_specs = [
            ("IT101", "Introduction to Computing", 3, bsit),
            ("IT102", "Computer Programming 1", 3, bsit),
            ("IT201", "Data Structures and Algorithms", 3, bsit),
            ("CS101", "Computer Science Fundamentals", 3, bscs),
            ("BA101", "Principles of Management", 3, bsba),
            ("GE101", "Understanding the Self", 3, None),
            ("GE102", "Mathematics in the Modern World", 3, None),
            ("PE101", "Physical Fitness", 2, None),
            ("NSTP101", "National Service Training Program 1", 3, None),
        ]
        subjects = {}
        for code, title, units, program in subject_specs:
            subject, _ = Subject.objects.get_or_create(
                code=code,
                defaults={"title": title, "units": units, "program": program},
            )
            subjects[code] = subject

        section_specs = [
            ("IT101", "A", "MWF 8:00-9:00 AM", "Lab 201", "Prof. A. Cruz", 40),
            ("IT101", "B", "TTh 9:30-11:00 AM", "Lab 202", "Prof. R. Lim", 40),
            ("IT102", "A", "MWF 9:30-10:30 AM", "Lab 203", "Prof. J. Reyes", 40),
            ("IT201", "A", "TTh 1:00-2:30 PM", "Lab 204", "Prof. S. Garcia", 35),
            ("CS101", "A", "MWF 10:45-11:45 AM", "Room 301", "Prof. M. Bautista", 40),
            ("BA101", "A", "TTh 8:00-9:30 AM", "Room 302", "Prof. L. Mendoza", 45),
            ("GE101", "A", "MWF 1:00-2:00 PM", "Room 101", "Prof. E. Villanueva", 50),
            ("GE101", "B", "TTh 2:30-4:00 PM", "Room 102", "Prof. E. Villanueva", 50),
            ("GE102", "A", "MWF 11:45-12:45 PM", "Room 103", "Prof. D. Aquino", 50),
            ("PE101", "A", "F 2:00-4:00 PM", "Gym", "Coach P. Ramos", 60),
            ("NSTP101", "A", "S 8:00-11:00 AM", "Room 201", "Prof. C. Navarro", 50),
        ]
        sections = {}
        for subject_code, code, schedule, room, instructor, capacity in section_specs:
            section, _ = Section.objects.get_or_create(
                subject=subjects[subject_code],
                term=term,
                code=code,
                defaults={
                    "schedule": schedule,
                    "room": room,
                    "instructor": instructor,
                    "capacity": capacity,
                },
            )
            sections[f"{subject_code}-{code}"] = section

        maria_profile = self._profile(maria, bsit, 1)
        juan_profile = self._profile(juan, bsit, 1)

        maria_app, created = Application.objects.get_or_create(
            student=maria_profile,
            term=term,
            defaults={
                "program": bsit,
                "year_level": StudentProfile.YearLevel.FIRST,
                "application_type": Application.Type.NEW,
                "previous_school": "Cavite National High School",
                "general_average": Decimal("92.50"),
                "personal_statement": (
                    "I want to build software that helps small businesses in my community. "
                    "The BSIT program will help me turn that goal into a career."
                ),
                "status": Application.Status.PENDING,
            },
        )
        if created:
            self.stdout.write("  Created Maria's pending application.")

        juan_app, created = Application.objects.get_or_create(
            student=juan_profile,
            term=term,
            defaults={
                "program": bsit,
                "year_level": StudentProfile.YearLevel.FIRST,
                "application_type": Application.Type.NEW,
                "previous_school": "St. Mary's Academy",
                "general_average": Decimal("89.25"),
                "personal_statement": (
                    "I enjoy solving problems with computers and want to specialize in "
                    "networking and cybersecurity."
                ),
                "status": Application.Status.APPROVED,
                "remarks": "Credentials verified. Welcome to BSIT.",
                "reviewed_by": admin,
                "reviewed_at": timezone.now(),
            },
        )

        enrollment, created = Enrollment.objects.get_or_create(
            student=juan_profile,
            term=term,
            defaults={
                "application": juan_app,
                "status": Enrollment.Status.PENDING,
            },
        )
        if created:
            for key in ("IT101-A", "IT102-A", "GE101-A", "PE101-A"):
                EnrollmentSubject.objects.create(
                    enrollment=enrollment, section=sections[key]
                )
            self.stdout.write("  Created Juan's pending enrollment.")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("")
        self.stdout.write("  Admin    admin@example.com   / Admin12345!")
        self.stdout.write("  Student  student@example.com / Student12345!  (pending application)")
        self.stdout.write("  Student  juan@example.com    / Student12345!  (approved, pending enrollment)")
        self.stdout.write("")

    def _ensure_user(self, email, password, full_name, role):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"full_name": full_name, "role": role},
        )
        if created:
            user.set_password(password)

        changed = False
        if user.full_name != full_name:
            user.full_name = full_name
            changed = True
        if user.role != role:
            user.role = role
            changed = True
        if role == User.Role.ADMIN and (not user.is_staff or not user.is_superuser):
            user.is_staff = True
            user.is_superuser = True
            changed = True
        if created or changed:
            user.save()
        return user

    def _profile(self, user, program, year_level):
        profile, _ = StudentProfile.objects.get_or_create(user=user)
        changed = False
        if profile.program_id != program.pk:
            profile.program = program
            changed = True
        if profile.year_level != year_level:
            profile.year_level = year_level
            changed = True
        if changed:
            profile.save(update_fields=["program", "year_level"])
        return profile
