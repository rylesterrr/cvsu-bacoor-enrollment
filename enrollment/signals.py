from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import StudentProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_student_profile(sender, instance, **kwargs):
    """Every student gets a profile (and a student number) automatically."""
    if getattr(instance, "role", None) != "STUDENT":
        return

    profile, _ = StudentProfile.objects.get_or_create(user=instance)
    if not profile.student_number:
        profile.student_number = f"{timezone.localdate().year}-{profile.pk:05d}"
        profile.save(update_fields=["student_number"])
