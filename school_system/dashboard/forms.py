from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Course


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=CustomUser.ROLES,
        widget=forms.RadioSelect
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'role', 'unique_id']

        
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'teacher', 'students']
        widgets = {
            'students': forms.CheckboxSelectMultiple
        }
