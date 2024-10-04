from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from .models import Student


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()

class SearchFacultyForm(forms.Form):
    filter = forms.ChoiceField(
        choices=[
            ('', '-- Select Filter --'),
            ('lab_name', 'Lab Name'),
            ('lab_code', 'Lab Code'),
            ('faculty_incharges', 'Faculty Incharges'),
            ('fi', 'FI'),
            ('faculty_id', 'Faculty ID'),
            ('department', 'Department'),
            ('designation', 'Designation'),
            ('email', 'Email'),
            ('contact_no', 'Contact No'),
        ],
        required=False
    )
    search = forms.CharField(required=False)
class SearchStudentForm(forms.Form):
    roll_no = forms.CharField(required=False)
    student_name = forms.CharField(required=False)
    student_email = forms.EmailField(required=False)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class StudentCardForm(forms.Form):
    roll_no = forms.CharField(max_length=100, required=True, label='Roll Number')
class OnDutyForm(forms.Form):
    lab_name = forms.CharField(max_length=100, required=True)
    from_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    purpose = forms.CharField(widget=forms.Textarea, required=True)

class OnDutySearchForm(forms.Form):
    lab_name = forms.ChoiceField(choices=[('All', 'All')] + [(name, name) for name in Student.objects.values_list('lab_name', flat=True).distinct()], required=False)
    from_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    to_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))