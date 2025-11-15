from django import forms
from django.core.exceptions import ValidationError
from student.models import Department, Program


class DeanStudentForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First name')
    last_name = forms.CharField(max_length=150, label='Last name')
    email = forms.EmailField(label='Email')
    student_id = forms.CharField(max_length=20, label='Student ID')
    phone = forms.CharField(max_length=20, required=False, label='Phone')
    department = forms.ModelChoiceField(queryset=Department.objects.none(), label='Department')
    program = forms.ModelChoiceField(queryset=Program.objects.none(), label='Program')
    current_year = forms.ChoiceField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4'), (5, 'Year 5')], label='Current Year')
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Date of Birth')
    address = forms.CharField(widget=forms.Textarea, required=False, label='Address')
    photo = forms.ImageField(required=False, label='Profile Photo')

    def __init__(self, faculty=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit departments and programs to the provided faculty if given
        if faculty is not None:
            self.fields['department'].queryset = Department.objects.filter(faculty=faculty)
            self.fields['program'].queryset = Program.objects.filter(department__faculty=faculty)
        else:
            self.fields['department'].queryset = Department.objects.all()
            self.fields['program'].queryset = Program.objects.all()

        # Ensure consistent Bootstrap classes on widgets
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.NullBooleanSelect)) or getattr(field, 'choices', None):
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-select').strip()
            elif isinstance(widget, (forms.Textarea,)):
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-control').strip()
            else:
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = (existing + ' form-control').strip()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        from django.contrib.auth.models import User
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with that email already exists.')
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data.get('student_id')
        from student.models import Student
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError('A student with that student ID already exists.')
        return student_id


class DeanProgramForm(forms.Form):
    name = forms.CharField(max_length=100, label='Program Name')
    code = forms.CharField(max_length=20, label='Program Code')
    department = forms.ModelChoiceField(queryset=Department.objects.none(), label='Department')
    description = forms.CharField(widget=forms.Textarea, required=False, label='Description')

    def __init__(self, faculty=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty is not None:
            self.fields['department'].queryset = Department.objects.filter(faculty=faculty)
        else:
            self.fields['department'].queryset = Department.objects.all()

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Program.objects.filter(code=code).exists():
            raise ValidationError('A program with that code already exists.')
        return code
