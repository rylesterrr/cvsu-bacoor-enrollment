from django.contrib import admin

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


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = [
        "school_year",
        "semester",
        "is_active",
        "enrollment_open",
        "enrollment_deadline",
    ]
    list_filter = ["is_active", "enrollment_open", "semester"]
    search_fields = ["school_year"]


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["student_number", "user", "program", "year_level"]
    list_filter = ["program", "year_level"]
    search_fields = ["student_number", "user__full_name", "user__email"]
    autocomplete_fields = ["user"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["student", "term", "program", "status", "submitted_at"]
    list_filter = ["status", "term", "program", "application_type"]
    search_fields = [
        "student__student_number",
        "student__user__full_name",
        "student__user__email",
    ]
    autocomplete_fields = ["student", "program", "term"]
    readonly_fields = ["submitted_at", "reviewed_at", "updated_at"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["code", "title", "units", "program"]
    list_filter = ["program"]
    search_fields = ["code", "title"]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["subject", "term", "code", "schedule", "capacity"]
    list_filter = ["term", "subject__program"]
    search_fields = ["subject__code", "subject__title"]
    autocomplete_fields = ["subject", "term"]


class EnrollmentSubjectInline(admin.TabularInline):
    model = EnrollmentSubject
    extra = 0
    autocomplete_fields = ["section"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        "reference_code",
        "student",
        "term",
        "status",
        "submitted_at",
    ]
    list_filter = ["status", "term"]
    search_fields = [
        "reference_code",
        "student__student_number",
        "student__user__full_name",
    ]
    autocomplete_fields = ["student", "term", "application"]
    readonly_fields = ["reference_code", "submitted_at", "updated_at"]
    inlines = [EnrollmentSubjectInline]
