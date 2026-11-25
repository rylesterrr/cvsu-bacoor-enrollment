from django.test import TestCase
from django.urls import reverse

from enrollment.models import StudentProfile

from .models import User


class RegistrationTests(TestCase):
    def test_student_registration_creates_profile_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Test Student",
                "email": "test.student@example.com",
                "password1": "CvSU!2026",
                "password2": "CvSU!2026",
            },
        )

        self.assertRedirects(response, reverse("enrollment:dashboard"))
        user = User.objects.get(email="test.student@example.com")
        self.assertEqual(user.role, User.Role.STUDENT)
        profile = StudentProfile.objects.get(user=user)
        self.assertTrue(profile.student_number)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            email="taken@example.com", password="CvSU!2026", full_name="Existing"
        )
        response = self.client.post(
            reverse("accounts:register"),
            {
                "full_name": "Another Student",
                "email": "taken@example.com",
                "password1": "CvSU!2026",
                "password2": "CvSU!2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email="taken@example.com").count(), 1)


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="login@example.com",
            password="CvSU!2026",
            full_name="Login User",
        )

    def test_login_with_email(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "login@example.com", "password": "CvSU!2026"},
        )
        self.assertRedirects(response, reverse("enrollment:dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("enrollment:dashboard"))
        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('enrollment:dashboard')}",
        )
