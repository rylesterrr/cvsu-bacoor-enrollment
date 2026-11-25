from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm, StudentRegistrationForm


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("enrollment:dashboard")

    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome, {user.full_name.split()[0]}! Your student account is ready.",
            )
            return redirect("enrollment:dashboard")
    else:
        form = StudentRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    from enrollment.forms import StudentProfileForm
    from enrollment.models import StudentProfile

    if request.user.is_administrator:
        return render(
            request,
            "accounts/profile.html",
            {"form": None, "student_profile": None},
        )

    student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = StudentProfileForm(instance=student_profile)

    return render(
        request,
        "accounts/profile.html",
        {"form": form, "student_profile": student_profile},
    )
