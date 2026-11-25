import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required, student_required

from .forms import ApplicationForm, EnrollmentStatusForm, ReviewApplicationForm
from .models import (
    Application,
    Enrollment,
    EnrollmentSubject,
    Program,
    Section,
    StudentProfile,
    Term,
)

logger = logging.getLogger(__name__)

MAX_UNITS_PER_TERM = 24


def active_term():
    """Return the term currently advertised to students."""
    return Term.objects.filter(is_active=True).order_by("-school_year", "semester").first()


def sections_for_term(term):
    """Sections with a live count of enrolled students (one query)."""
    return (
        Section.objects.filter(term=term)
        .select_related("subject", "subject__program")
        .annotate(
            taken=Count(
                "enrollment_subjects",
                filter=Q(
                    enrollment_subjects__status=EnrollmentSubject.Status.ENROLLED,
                    enrollment_subjects__enrollment__status__in=Enrollment.ACTIVE_STATUSES,
                ),
            )
        )
        .order_by("subject__code", "code")
    )


def home(request):
    if request.user.is_authenticated:
        return redirect("enrollment:dashboard")

    term = active_term()
    return render(
        request,
        "public/landing.html",
        {
            "term": term,
            "programs": Program.objects.filter(is_active=True),
        },
    )


@login_required
def dashboard(request):
    if request.user.is_administrator:
        return _admin_dashboard(request)
    return _student_dashboard(request)


def _student_dashboard(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    term = active_term()
    application = None
    enrollment = None
    available_sections = 0

    if term:
        application = (
            Application.objects.filter(student=profile, term=term)
            .select_related("program")
            .first()
        )
        enrollment = (
            Enrollment.objects.filter(student=profile, term=term)
            .prefetch_related("subjects__section__subject")
            .first()
        )
        available_sections = sections_for_term(term).count()

    return render(
        request,
        "enrollment/student_dashboard.html",
        {
            "profile": profile,
            "term": term,
            "application": application,
            "enrollment": enrollment,
            "available_sections": available_sections,
            "max_units": MAX_UNITS_PER_TERM,
        },
    )


def _admin_dashboard(request):
    term = active_term()
    counts = {
        "pending_applications": Application.objects.filter(
            status=Application.Status.PENDING
        ).count(),
        "under_review": Application.objects.filter(
            status=Application.Status.UNDER_REVIEW
        ).count(),
        "approved_applications": Application.objects.filter(
            status=Application.Status.APPROVED
        ).count(),
        "pending_enrollments": Enrollment.objects.filter(
            status=Enrollment.Status.PENDING
        ).count(),
        "enrolled_students": Enrollment.objects.filter(
            status=Enrollment.Status.ENROLLED
        )
        .values("student")
        .distinct()
        .count(),
    }
    recent_applications = (
        Application.objects.select_related("student__user", "program", "term")
        .order_by("-submitted_at")[:6]
    )
    recent_enrollments = (
        Enrollment.objects.select_related("student__user", "term")
        .annotate(
            units_total=Sum(
                "subjects__section__subject__units",
                filter=Q(subjects__status=EnrollmentSubject.Status.ENROLLED),
            )
        )
        .order_by("-submitted_at")[:5]
    )

    return render(
        request,
        "enrollment/admin_dashboard.html",
        {
            "term": term,
            "counts": counts,
            "recent_applications": recent_applications,
            "recent_enrollments": recent_enrollments,
        },
    )


# ---------------------------------------------------------------------------
# Student: application
# ---------------------------------------------------------------------------
@student_required
def apply(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    term = active_term()

    if term is None:
        messages.error(request, "There is no active term yet. Please check back later.")
        return redirect("enrollment:dashboard")

    if not term.is_accepting_enrollment:
        messages.error(request, f"Enrollment is closed for {term}.")
        return redirect("enrollment:dashboard")

    application = Application.objects.filter(student=profile, term=term).first()
    if application and not application.can_edit:
        messages.info(request, "This application can no longer be edited.")
        return redirect("enrollment:application_detail", pk=application.pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.student = profile
            app.term = term
            app.status = Application.Status.PENDING
            app.reviewed_at = None
            app.reviewed_by = None
            app.remarks = ""
            app.save()

            if profile.program_id is None:
                profile.program = app.program
                profile.year_level = app.year_level
                profile.save(update_fields=["program", "year_level"])

            messages.success(
                request,
                "Application submitted. You can track its status from your dashboard.",
            )
            return redirect("enrollment:application_detail", pk=app.pk)
    else:
        initial = {}
        if application is None and profile.program_id:
            initial = {"program": profile.program, "year_level": profile.year_level}
        form = ApplicationForm(instance=application, initial=initial)

    return render(
        request,
        "enrollment/apply.html",
        {"form": form, "term": term, "application": application},
    )


@student_required
def application_status(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    applications = (
        Application.objects.filter(student=profile)
        .select_related("term", "program", "reviewed_by")
        .order_by("-submitted_at")
    )
    term = active_term()
    current_application = (
        applications.filter(term=term).first() if term else None
    )
    return render(
        request,
        "enrollment/application_status.html",
        {
            "applications": applications,
            "term": term,
            "current_application": current_application,
        },
    )


@student_required
def application_detail(request, pk):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    application = get_object_or_404(
        Application.objects.select_related("term", "program", "reviewed_by"),
        pk=pk,
        student=profile,
    )
    enrollment = Enrollment.objects.filter(student=profile, term=application.term).first()
    return render(
        request,
        "enrollment/application_detail.html",
        {"application": application, "enrollment": enrollment},
    )


# ---------------------------------------------------------------------------
# Student: enrollment
# ---------------------------------------------------------------------------
@student_required
def enroll(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    term = active_term()

    context = {
        "profile": profile,
        "term": term,
        "max_units": MAX_UNITS_PER_TERM,
        "sections": [],
        "selected_ids": [],
        "errors": [],
    }

    if term is None:
        context["blocked_reason"] = "There is no active term yet."
        return render(request, "enrollment/enroll.html", context)

    application = (
        Application.objects.filter(student=profile, term=term)
        .select_related("program")
        .first()
    )
    existing = Enrollment.objects.filter(student=profile, term=term).first()

    context["application"] = application

    if existing:
        messages.info(request, "You already have an enrollment for this term.")
        return redirect("enrollment:enrollment_status")

    if not term.is_accepting_enrollment:
        context["blocked_reason"] = f"Enrollment is closed for {term}."
        return render(request, "enrollment/enroll.html", context)

    if application is None:
        context["blocked_reason"] = "Submit an application first. Enrollment opens once it is approved."
        return render(request, "enrollment/enroll.html", context)

    if not application.is_approved:
        context["blocked_reason"] = (
            "Your application is not approved yet. You can enroll after the registrar approves it."
        )
        return render(request, "enrollment/enroll.html", context)

    if request.method == "POST":
        selected_ids = request.POST.getlist("sections")
        errors = []

        if not selected_ids:
            errors.append("Select at least one section.")
        elif len(selected_ids) != len(set(selected_ids)):
            errors.append("A section was selected more than once.")

        if not errors:
            try:
                with transaction.atomic():
                    sections = list(
                        Section.objects.select_for_update()
                        .filter(pk__in=selected_ids, term=term)
                        .select_related("subject")
                    )

                    if len(sections) != len(set(selected_ids)):
                        errors.append("One of the selected sections is no longer available.")

                    total_units = sum(section.subject.units for section in sections)
                    if total_units > MAX_UNITS_PER_TERM:
                        errors.append(
                            f"You selected {total_units} units. The maximum is "
                            f"{MAX_UNITS_PER_TERM} units per term."
                        )

                    for section in sections:
                        if section.enrolled_count >= section.capacity:
                            errors.append(
                                f"{section.subject.code} Section {section.code} is already full."
                            )

                    if not errors:
                        enrollment = Enrollment.objects.create(
                            student=profile,
                            term=term,
                            application=application,
                            status=Enrollment.Status.PENDING,
                        )
                        EnrollmentSubject.objects.bulk_create(
                            [
                                EnrollmentSubject(enrollment=enrollment, section=section)
                                for section in sections
                            ]
                        )
            except IntegrityError:
                logger.exception("Enrollment could not be saved for student %s", profile.pk)
                errors.append("We could not save your enrollment. Please try again.")

        if errors:
            context["errors"] = errors
            context["selected_ids"] = selected_ids
        else:
            messages.success(
                request,
                "Enrollment submitted. The registrar will confirm your subjects shortly.",
            )
            return redirect("enrollment:enrollment_status")

    context["sections"] = sections_for_term(term)
    return render(request, "enrollment/enroll.html", context)


@student_required
def enrollment_status(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    term = active_term()
    enrollments = (
        Enrollment.objects.filter(student=profile)
        .select_related("term", "application")
        .prefetch_related("subjects__section__subject")
        .order_by("-submitted_at")
    )
    current = None
    if term:
        current = enrollments.filter(term=term).first()
    if current is None:
        current = enrollments.first()

    return render(
        request,
        "enrollment/enrollment_status.html",
        {"enrollments": enrollments, "current": current, "term": term},
    )


@login_required
def subjects(request):
    term = active_term()
    sections = sections_for_term(term) if term else Section.objects.none()
    return render(
        request,
        "enrollment/subjects.html",
        {"term": term, "sections": sections},
    )


# ---------------------------------------------------------------------------
# Administrator: applications and enrollments
# ---------------------------------------------------------------------------
@admin_required
def manage_applications(request):
    status = request.GET.get("status", "")
    valid_statuses = {value for value, _ in Application.Status.choices}

    applications = Application.objects.select_related(
        "student__user", "program", "term"
    ).order_by("-submitted_at")
    if status in valid_statuses:
        applications = applications.filter(status=status)

    count_map = {
        row["status"]: row["total"]
        for row in Application.objects.values("status").annotate(total=Count("id"))
    }
    total = Application.objects.count()
    tabs = [{"value": "", "label": "All", "count": total}]
    tabs += [
        {
            "value": value,
            "label": label,
            "count": count_map.get(value, 0),
        }
        for value, label in Application.Status.choices
    ]

    return render(
        request,
        "enrollment/manage_applications.html",
        {
            "applications": applications,
            "tabs": tabs,
            "active_status": status,
            "term": active_term(),
        },
    )


@admin_required
def review_application(request, pk):
    application = get_object_or_404(
        Application.objects.select_related("student__user", "program", "term"), pk=pk
    )

    if request.method == "POST":
        form = ReviewApplicationForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data["status"]
            application.status = new_status
            application.remarks = form.cleaned_data["remarks"]
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save(
                update_fields=["status", "remarks", "reviewed_by", "reviewed_at", "updated_at"]
            )
            messages.success(
                request,
                f"Application for {application.student.user.full_name} is now "
                f"{application.get_status_display().lower()}.",
            )
            return redirect("enrollment:manage_applications")
    else:
        initial_status = application.status
        if initial_status not in {
            Application.Status.UNDER_REVIEW,
            Application.Status.APPROVED,
            Application.Status.WAITLISTED,
            Application.Status.REJECTED,
        }:
            initial_status = Application.Status.UNDER_REVIEW
        form = ReviewApplicationForm(
            initial={"status": initial_status, "remarks": application.remarks}
        )

    return render(
        request,
        "enrollment/review_application.html",
        {"application": application, "form": form},
    )


@admin_required
def manage_enrollments(request):
    status = request.GET.get("status", "")
    valid_statuses = {value for value, _ in Enrollment.Status.choices}

    enrollments = (
        Enrollment.objects.select_related("student__user", "term")
        .annotate(
            units_total=Sum(
                "subjects__section__subject__units",
                filter=Q(subjects__status=EnrollmentSubject.Status.ENROLLED),
            )
        )
        .order_by("-submitted_at")
    )
    if status in valid_statuses:
        enrollments = enrollments.filter(status=status)

    count_map = {
        row["status"]: row["total"]
        for row in Enrollment.objects.values("status").annotate(total=Count("id"))
    }
    total = Enrollment.objects.count()
    tabs = [{"value": "", "label": "All", "count": total}]
    tabs += [
        {"value": value, "label": label, "count": count_map.get(value, 0)}
        for value, label in Enrollment.Status.choices
    ]

    return render(
        request,
        "enrollment/manage_enrollments.html",
        {
            "enrollments": enrollments,
            "tabs": tabs,
            "active_status": status,
            "status_form": EnrollmentStatusForm(),
            "term": active_term(),
        },
    )


@admin_required
@require_POST
def update_enrollment_status(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    form = EnrollmentStatusForm(request.POST)
    if form.is_valid():
        enrollment.status = form.cleaned_data["status"]
        enrollment.save(update_fields=["status", "updated_at"])
        messages.success(
            request,
            f"{enrollment.reference_code} is now {enrollment.get_status_display().lower()}.",
        )
    else:
        messages.error(request, "That enrollment status is not valid.")
    return redirect("enrollment:manage_enrollments")
