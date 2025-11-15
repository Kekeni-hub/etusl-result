from django import forms
from django.core.exceptions import ValidationError
from student.models import Faculty, Department, Program, Student


class OfficerStudentForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First name')
    last_name = forms.CharField(max_length=150, label='Last name')
    email = forms.EmailField(label='Email')
    student_id = forms.CharField(max_length=20, label='Student ID')
    phone = forms.CharField(max_length=20, required=False, label='Phone')
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), label='Faculty')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department')
    program = forms.ModelChoiceField(queryset=Program.objects.all(), label='Program')
    current_year = forms.ChoiceField(choices=[(1, 'Year 1'), (2, 'Year 2'), (3, 'Year 3'), (4, 'Year 4'), (5, 'Year 5')], label='Current Year')
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Date of Birth')
    address = forms.CharField(widget=forms.Textarea, required=False, label='Address')
    photo = forms.ImageField(required=False, label='Profile Photo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure consistent Bootstrap classes on widgets
        for name, field in self.fields.items():
            widget = field.widget
            # Apply form-select for choice/modelchoice widgets
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
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError('A student with that student ID already exists.')
        return student_id

    def clean(self):
        cleaned = super().clean()
        dept = cleaned.get('department')
        fac = cleaned.get('faculty')
        prog = cleaned.get('program')
        if dept and fac and dept.faculty != fac:
            raise ValidationError('Selected department does not belong to the selected faculty.')
        if prog and dept and prog.department != dept:
            raise ValidationError('Selected program does not belong to the selected department.')
        return cleaned


class OfficerProgramForm(forms.Form):
    name = forms.CharField(max_length=100, label='Program Name')
    code = forms.CharField(max_length=20, label='Program Code')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department')
    description = forms.CharField(widget=forms.Textarea, required=False, label='Description')

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if Program.objects.filter(code=code).exists():
            raise ValidationError('A program with that code already exists.')
        return code
