from django import forms
from django.core.exceptions import ValidationError
from .models import Lecturer
from student.models import Faculty, Department


class LecturerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, label='First name')
    last_name = forms.CharField(max_length=150, label='Last name')
    email = forms.EmailField(label='Email')

    class Meta:
        model = Lecturer
        fields = ['phone', 'faculty', 'department', 'specialization', 'office_location', 'bio']

    def __init__(self, *args, **kwargs):
        # Expect an instance of Lecturer to be passed as instance=...
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to widgets
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select,)) or getattr(field, 'choices', None):
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-select').strip()
            elif isinstance(widget, (forms.Textarea,)):
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-control').strip()
            else:
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-control').strip()

    def clean_email(self):
        # email validation will be handled when saving User; leave here for completeness
        return self.cleaned_data.get('email')

    def save(self, commit=True):
        # Update Lecturer model, and also update related User fields (first/last/email)
        lecturer = super().save(commit=False)
        email = self.cleaned_data.get('email')
        first = self.cleaned_data.get('first_name')
        last = self.cleaned_data.get('last_name')

        user = lecturer.user
        if email and user.email != email:
            user.email = email
            user.username = email  # keep username in sync
        if first:
            user.first_name = first
        if last:
            user.last_name = last

        if commit:
            user.save()
            lecturer.save()
        else:
            # caller will save later
            lecturer.user = user
        return lecturer
