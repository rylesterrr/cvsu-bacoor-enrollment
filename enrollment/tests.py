from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import (
    Application,
    Enrollment,
    EnrollmentSubject,
    Program,
    Section,
    StudentProfile,
    Subject,
    Term,
)


class EnrollmentTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.program = Program.objects.create(code="BSIT", name="Information Technology")
        cls.term = Term.objects.create(
            school_year="2026-2027",
            semester=Term.Semester.FIRST,
            enrollment_open=True,
            is_active=True,
        )
        cls.subject = Subject.objects.create(
            code="IT101", title="Introduction to Computing", units=3, program=cls.program
        )
        cls.section = Section.objects.create(
            subject=cls.subject,
            term=cls.term,
            code="A",
            schedule="MWF 8:00-9:00 AM",
            capacity=40,
        )
        cls.admin = User.objects.create_user(
            email="admin@test.com",
            password="AdminPass!2026",
            full_name="Test Admin",
            role=User.Role.ADMIN,
            is_staff=True,
        )
        cls.student = User.objects.create_user(
            email="student@test.com",
            password="StudentPass!2026",
            full_name="Test Student",
            role=User.Role.STUDENT,
        )
        cls.profile = StudentProfile.objects.get(user=cls.student)
        cls.profile.program = cls.program
        cls.profile.save()
        cls.application = Application.objects.create(
            student=cls.profile,
            term=cls.term,
            program=cls.program,
            year_level=1,
            application_type=Application.Type.NEW,
            personal_statement="I want to study IT.",
            status=Application.Status.APPROVED,
        )


class StudentFlowTests(EnrollmentTestData):
    def setUp(self):
        self.client.force_login(self.student)

    def test_dashboard_loads(self):
        response = self.client.get(reverse("enrollment:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Dashboard")

    def test_student_cannot_open_registrar_pages(self):
        response = self.client.get(reverse("enrollment:manage_applications"))
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_open_student_enrollment(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("enrollment:enroll"))
        self.assertEqual(response.status_code, 403)

    def test_enrollment_submission(self):
        response = self.client.post(
            reverse("enrollment:enroll"), {"sections": [self.section.pk]}
        )
        self.assertRedirects(response, reverse("enrollment:enrollment_status"))

        enrollment = Enrollment.objects.get(student=self.profile, term=self.term)
        self.assertEqual(enrollment.status, Enrollment.Status.PENDING)
        self.assertTrue(enrollment.reference_code.startswith("ENR-"))
        self.assertEqual(enrollment.subjects.count(), 1)

    def test_enrollment_requires_approved_application(self):
        self.application.status = Application.Status.PENDING
        self.application.save(update_fields=["status"])

        response = self.client.post(
            reverse("enrollment:enroll"), {"sections": [self.section.pk]}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not approved yet")
        self.assertFalse(Enrollment.objects.filter(student=self.profile).exists())

    def test_full_section_is_rejected(self):
        self.section.capacity = 1
        self.section.save(update_fields=["capacity"])

        other = User.objects.create_user(
            email="other@test.com",
            password="StudentPass!2026",
            full_name="Other Student",
            role=User.Role.STUDENT,
        )
        other_profile = StudentProfile.objects.get(user=other)
        other_enrollment = Enrollment.objects.create(
            student=other_profile, term=self.term, status=Enrollment.Status.PENDING
        )
        EnrollmentSubject.objects.create(
            enrollment=other_enrollment, section=self.section
        )

        response = self.client.post(
            reverse("enrollment:enroll"), {"sections": [self.section.pk]}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already full")
        self.assertFalse(Enrollment.objects.filter(student=self.profile).exists())

    def test_empty_selection_is_rejected(self):
        response = self.client.post(reverse("enrollment:enroll"), {"sections": []})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Select at least one section")
        self.assertFalse(Enrollment.objects.filter(student=self.profile).exists())


class ApplicationFlowTests(EnrollmentTestData):
    def setUp(self):
        self.new_student = User.objects.create_user(
            email="new@test.com",
            password="StudentPass!2026",
            full_name="New Student",
            role=User.Role.STUDENT,
        )
        self.new_profile = StudentProfile.objects.get(user=self.new_student)
        self.client.force_login(self.new_student)

    def test_apply_creates_pending_application(self):
        response = self.client.post(
            reverse("enrollment:apply"),
            {
                "program": self.program.pk,
                "year_level": 1,
                "application_type": Application.Type.NEW,
                "previous_school": "Test High School",
                "general_average": "91.50",
                "personal_statement": "I would like to join the IT program.",
            },
        )

        application = Application.objects.get(
            student=self.new_profile, term=self.term
        )
        self.assertRedirects(
            response, reverse("enrollment:application_detail", args=[application.pk])
        )
        self.assertEqual(application.status, Application.Status.PENDING)
        self.new_profile.refresh_from_db()
        self.assertEqual(self.new_profile.program, self.program)


class AdminFlowTests(EnrollmentTestData):
    def setUp(self):
        self.client.force_login(self.admin)

    def test_admin_dashboard_loads(self):
        response = self.client.get(reverse("enrollment:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registrar dashboard")

    def test_approve_application(self):
        response = self.client.post(
            reverse("enrollment:review_application", args=[self.application.pk]),
            {"status": Application.Status.APPROVED, "remarks": "Looks good."},
        )
        self.assertRedirects(response, reverse("enrollment:manage_applications"))

        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.APPROVED)
        self.assertEqual(self.application.reviewed_by, self.admin)
        self.assertIsNotNone(self.application.reviewed_at)

    def test_confirm_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.profile, term=self.term, status=Enrollment.Status.PENDING
        )
        response = self.client.post(
            reverse("enrollment:update_enrollment_status", args=[enrollment.pk]),
            {"status": Enrollment.Status.ENROLLED},
        )
        self.assertRedirects(response, reverse("enrollment:manage_enrollments"))

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, Enrollment.Status.ENROLLED)

    def test_student_cannot_review_applications(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("enrollment:review_application", args=[self.application.pk])
        )
        self.assertEqual(response.status_code, 403)


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_creates_accounts_and_term(self):
        call_command("seed_demo", verbosity=0)

        self.assertTrue(User.objects.filter(email="admin@example.com").exists())
        self.assertTrue(User.objects.filter(email="student@example.com").exists())
        self.assertTrue(User.objects.filter(email="juan@example.com").exists())
        self.assertTrue(Term.objects.filter(is_active=True).exists())
        self.assertTrue(Application.objects.exists())
        self.assertTrue(Enrollment.objects.exists())


class PublicSiteTests(TestCase):
    def test_landing_page_loads_for_anonymous_users(self):
        response = self.client.get(reverse("enrollment:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cavite State University")
        self.assertContains(response, "Bacoor City Campus")

    def test_authenticated_user_is_redirected_to_dashboard(self):
        user = User.objects.create_user(
            email="landing@test.com",
            password="LandingPass!2026",
            full_name="Landing User",
            role=User.Role.STUDENT,
        )
        self.client.force_login(user)
        response = self.client.get(reverse("enrollment:home"))
        self.assertRedirects(response, reverse("enrollment:dashboard"))
