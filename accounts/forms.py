from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={
                "class": "input",
                "autocomplete": "email",
                "placeholder": "you@school.edu",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "input",
                "autocomplete": "current-password",
                "placeholder": "Enter your password",
            }
        ),
    )


class StudentRegistrationForm(UserCreationForm):
    """Public sign-up is for students only. Administrators are created in Django admin."""

    class Meta:
        model = User
        fields = ("full_name", "email")
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "input",
                    "autocomplete": "name",
                    "placeholder": "Juan Dela Cruz",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input",
                    "autocomplete": "email",
                    "placeholder": "you@school.edu",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].label = "Full name"
        self.fields["password1"].widget.attrs.update(
            {"class": "input", "autocomplete": "new-password", "placeholder": "At least 8 characters"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "input", "autocomplete": "new-password", "placeholder": "Repeat your password"}
        )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user
