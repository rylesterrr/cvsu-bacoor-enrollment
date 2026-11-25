from django.urls import path

from . import views

app_name = "enrollment"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Student application flow
    path("apply/", views.apply, name="apply"),
    path("application/", views.application_status, name="application_status"),
    path("application/<int:pk>/", views.application_detail, name="application_detail"),
    # Student enrollment flow
    path("enroll/", views.enroll, name="enroll"),
    path("enrollment/", views.enrollment_status, name="enrollment_status"),
    path("subjects/", views.subjects, name="subjects"),
    # Registrar / administrator
    path("manage/applications/", views.manage_applications, name="manage_applications"),
    path(
        "manage/applications/<int:pk>/",
        views.review_application,
        name="review_application",
    ),
    path("manage/enrollments/", views.manage_enrollments, name="manage_enrollments"),
    path(
        "manage/enrollments/<int:pk>/status/",
        views.update_enrollment_status,
        name="update_enrollment_status",
    ),
]
