from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Program(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.name}"


class Term(models.Model):
    class Semester(models.TextChoices):
        FIRST = "1ST", "First Semester"
        SECOND = "2ND", "Second Semester"
        SUMMER = "SUM", "Summer"

    school_year = models.CharField(max_length=9, help_text="Example: 2026-2027")
    semester = models.CharField(max_length=3, choices=Semester.choices)
    enrollment_open = models.BooleanField(default=True)
    enrollment_deadline = models.DateField(null=True, blank=True)
    classes_start = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="The active term is shown on dashboards and used for new applications.",
    )

    class Meta:
        ordering = ["-school_year", "semester"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "semester"], name="unique_term_per_semester"
            )
        ]

    def __str__(self):
        return f"{self.school_year} · {self.get_semester_display()}"

    @property
    def is_accepting_enrollment(self):
        if not self.enrollment_open:
            return False
        if self.enrollment_deadline and self.enrollment_deadline < timezone.localdate():
            return False
        return True


class StudentProfile(models.Model):
    class YearLevel(models.IntegerChoices):
        FIRST = 1, "First year"
        SECOND = 2, "Second year"
        THIRD = 3, "Third year"
        FOURTH = 4, "Fourth year"
        FIFTH = 5, "Fifth year"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    student_number = models.CharField(max_length=20, unique=True, blank=True)
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )
    year_level = models.PositiveSmallIntegerField(
        choices=YearLevel.choices, default=YearLevel.FIRST
    )
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["student_number", "user__full_name"]
        verbose_name = "student profile"
        verbose_name_plural = "student profiles"

    def __str__(self):
        return f"{self.student_number or 'No number'} — {self.user.full_name}"


class Application(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending review"
        UNDER_REVIEW = "UNDER_REVIEW", "Under review"
        APPROVED = "APPROVED", "Approved"
        WAITLISTED = "WAITLISTED", "Waitlisted"
        REJECTED = "REJECTED", "Rejected"

    class Type(models.TextChoices):
        NEW = "NEW", "New student"
        TRANSFEREE = "TRANSFEREE", "Transferee"
        RETURNING = "RETURNING", "Returning student"

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="applications"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="applications")
    program = models.ForeignKey(
        Program, on_delete=models.PROTECT, related_name="applications"
    )
    year_level = models.PositiveSmallIntegerField(
        choices=StudentProfile.YearLevel.choices, default=StudentProfile.YearLevel.FIRST
    )
    application_type = models.CharField(
        max_length=12, choices=Type.choices, default=Type.NEW
    )
    previous_school = models.CharField(max_length=180, blank=True)
    general_average = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Optional. Use the 0–100 scale.",
    )
    personal_statement = models.TextField(
        help_text="Tell us briefly why you want to enroll in this program."
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    remarks = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "term"], name="unique_application_per_term"
            )
        ]

    def __str__(self):
        return f"{self.student.user.full_name} — {self.term}"

    @property
    def status_slug(self):
        return self.status.lower().replace("_", "-")

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    @property
    def can_edit(self):
        return self.status in {
            self.Status.DRAFT,
            self.Status.PENDING,
            self.Status.REJECTED,
            self.Status.WAITLISTED,
        }

    @property
    def status_note(self):
        return {
            self.Status.DRAFT: "Finish your details and submit the application.",
            self.Status.PENDING: "Your application is in the queue for review.",
            self.Status.UNDER_REVIEW: "An admissions officer is reviewing your application.",
            self.Status.APPROVED: "You are approved. You can now enroll in sections.",
            self.Status.WAITLISTED: "You are on the waitlist. We will update you soon.",
            self.Status.REJECTED: "Your application was not approved. You may edit and resubmit.",
        }.get(self.status, "")


class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=150)
    units = models.PositiveSmallIntegerField(default=3)
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects",
        help_text="Leave blank for general education subjects.",
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.title}"


class Section(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="sections")
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="sections")
    code = models.CharField(max_length=10, default="A", help_text="Section code, e.g. A or B.")
    schedule = models.CharField(max_length=120, help_text="Example: MWF 8:00–9:00 AM")
    room = models.CharField(max_length=60, blank=True)
    instructor = models.CharField(max_length=120, blank=True)
    capacity = models.PositiveSmallIntegerField(default=40)

    class Meta:
        ordering = ["subject__code", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "term", "code"], name="unique_section_per_term"
            )
        ]

    def __str__(self):
        return f"{self.subject.code} — Section {self.code}"

    @property
    def enrolled_count(self):
        return self.enrollment_subjects.filter(
            status=EnrollmentSubject.Status.ENROLLED,
            enrollment__status__in=Enrollment.ACTIVE_STATUSES,
        ).count()

    @property
    def slots_left(self):
        return max(self.capacity - self.enrolled_count, 0)

    @property
    def is_full(self):
        return self.slots_left <= 0


class Enrollment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending confirmation"
        ENROLLED = "ENROLLED", "Enrolled"
        DROPPED = "DROPPED", "Dropped"
        COMPLETED = "COMPLETED", "Completed"

    ACTIVE_STATUSES = ("PENDING", "ENROLLED")

    student = models.ForeignKey(
        StudentProfile, on_delete=models.CASCADE, related_name="enrollments"
    )
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name="enrollments")
    application = models.ForeignKey(
        Application,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reference_code = models.CharField(max_length=24, unique=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "term"], name="unique_enrollment_per_term"
            )
        ]

    def __str__(self):
        return f"{self.reference_code or 'Unsubmitted'} — {self.student.user.full_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.reference_code:
            self.reference_code = f"ENR-{timezone.now().year}-{self.pk:05d}"
            super().save(update_fields=["reference_code"])

    @property
    def status_slug(self):
        return self.status.lower().replace("_", "-")

    @property
    def is_active(self):
        return self.status in self.ACTIVE_STATUSES

    @property
    def total_units(self):
        return sum(
            item.section.subject.units
            for item in self.subjects.filter(status=EnrollmentSubject.Status.ENROLLED).select_related(
                "section__subject"
            )
        )

    @property
    def subject_count(self):
        return self.subjects.filter(status=EnrollmentSubject.Status.ENROLLED).count()

    @property
    def status_note(self):
        return {
            self.Status.PENDING: "Your enrollment is waiting for confirmation from the registrar.",
            self.Status.ENROLLED: "You are officially enrolled for this term.",
            self.Status.DROPPED: "This enrollment was dropped. Contact the registrar to re-enroll.",
            self.Status.COMPLETED: "This term has been completed.",
        }.get(self.status, "")


class EnrollmentSubject(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", "Enrolled"
        DROPPED = "DROPPED", "Dropped"

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="subjects"
    )
    section = models.ForeignKey(
        Section, on_delete=models.PROTECT, related_name="enrollment_subjects"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ENROLLED)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["section__subject__code"]
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "section"], name="unique_section_per_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.enrollment.reference_code} — {self.section}"
