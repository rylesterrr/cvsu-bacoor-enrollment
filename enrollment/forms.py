from django import forms

from .models import Application, Enrollment, StudentProfile


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ("program", "year_level", "phone", "address", "date_of_birth")
        widgets = {
            "program": forms.Select(attrs={"class": "input"}),
            "year_level": forms.Select(attrs={"class": "input"}),
            "phone": forms.TextInput(
                attrs={"class": "input", "placeholder": "+63 912 345 6789"}
            ),
            "address": forms.Textarea(
                attrs={"class": "input", "rows": 3, "placeholder": "City, province"}
            ),
            "date_of_birth": forms.DateInput(attrs={"class": "input", "type": "date"}),
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = (
            "program",
            "year_level",
            "application_type",
            "previous_school",
            "general_average",
            "personal_statement",
        )
        widgets = {
            "program": forms.Select(attrs={"class": "input"}),
            "year_level": forms.Select(attrs={"class": "input"}),
            "application_type": forms.Select(attrs={"class": "input"}),
            "previous_school": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Name of your previous school (optional)",
                }
            ),
            "general_average": forms.NumberInput(
                attrs={
                    "class": "input",
                    "placeholder": "e.g. 92.50",
                    "step": "0.01",
                    "min": "0",
                    "max": "100",
                }
            ),
            "personal_statement": forms.Textarea(
                attrs={
                    "class": "input",
                    "rows": 5,
                    "placeholder": "Share your goals and why this program is a good fit.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["previous_school"].required = False
        self.fields["general_average"].required = False


class ReviewApplicationForm(forms.Form):
    status = forms.ChoiceField(
        label="Decision",
        choices=[
            (Application.Status.UNDER_REVIEW, "Mark as under review"),
            (Application.Status.APPROVED, "Approve application"),
            (Application.Status.WAITLISTED, "Move to waitlist"),
            (Application.Status.REJECTED, "Reject application"),
        ],
        widget=forms.Select(attrs={"class": "input"}),
    )
    remarks = forms.CharField(
        label="Remarks",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "input",
                "rows": 4,
                "placeholder": "Optional notes visible to the student.",
            }
        ),
    )


class EnrollmentStatusForm(forms.Form):
    status = forms.ChoiceField(
        label="Enrollment status",
        choices=Enrollment.Status.choices,
        widget=forms.Select(attrs={"class": "input input-sm"}),
    )
