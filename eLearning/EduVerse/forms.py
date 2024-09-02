'''
The forms are linked to the User, Student, Teacher, Enrollment and Course models, and they are used to
update the model instances based on the user inputs. Each form has its fields defined and custom widgets
to control how these fields are rendered in the HTML page.

Reference: https://docs.djangoproject.com/en/5.1/ref/forms/widgets/#built-in-widgets,
https://docs.djangoproject.com/en/5.1/topics/forms/modelforms/,
https://www.geeksforgeeks.org/django-modelform-create-form-from-models/,
https://sayari3.com/articles/5-difference-between-django-formsform-and-formsmodelform/
'''

from django import forms
from .models import *

# user registration form, inheriting from ModelForm
class RegistrationForm(forms.ModelForm):
    # Creating a reusable password input widget
    PASSWORD_INPUT = forms.PasswordInput()
    
    # Password fields
    password = forms.CharField(widget=PASSWORD_INPUT, label="Password")
    confirm_password = forms.CharField(widget=PASSWORD_INPUT, label="Confirm Password")
    user_type = forms.ChoiceField(choices=User.ROLE_CHOICES, label="User Type")
    
    # Address fields
    street_address = forms.CharField(max_length=255, label="Street Address")
    post_code = forms.CharField(max_length=20, label="Post Code")
    city = forms.CharField(max_length=100, label="City")
    country = forms.CharField(max_length=100, label="Country")

    # Defines the model and the fields to include in the form
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'user_type', 'date_of_birth', 
                  'street_address', 'post_code', 'city', 'country']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    # This method adds a validation error to the form, 
    # which then prevents the form from being submitted
    # it raises an error if the password and confirm_password don't match
    def clean(self):
        # the clean method is called to remove any previous data
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

# Updating the student information, inheriting from ModelForm
class StudentUpdateForm(forms.ModelForm):
    # street_address, post_code, city and country are the information to be updated
    # defined with attributes and widgets
    # all fields are optional, there fore the forms can be updated only with one field
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the street address'}),
        required=False
    )
    post_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the post code'}),
        required=False
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the city'}),
        required=False
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the country'}),
        required=False
    )
    
    # the form is linked to the Student Model
    # ['profile_picture', 'street_address', 'post_code', 'city', 'country'] are the fields to be updated
    class Meta:
        model = Student
        fields = ['profile_picture', 'street_address', 'post_code', 'city', 'country']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

# this class creates or updates course information, inheriting from ModelForm
class CourseForm(forms.ModelForm):
    # the form is linked to the Course Model
    class Meta:
        model = Course
        fields = ['course_name', 'course_start_date', 'course_length', 'midterm_deadline', 'final_deadline', 'materials']
        widgets = {
            'course_name': forms.TextInput(attrs={'placeholder': 'Enter the course name'}),
            'course_start_date': forms.DateInput(attrs={'placeholder': 'Enter the course start date', 'type': 'date'}),
            'course_length': forms.NumberInput(attrs={'placeholder': 'Enter the course length in weeks'}),
            'midterm_deadline': forms.DateInput(attrs={'placeholder': 'Enter the midterm deadline', 'type': 'date'}),
            'final_deadline': forms.DateInput(attrs={'placeholder': 'Enter the final deadline', 'type': 'date'}),
            'materials': forms.ClearableFileInput(attrs={'multiple': False}),
        }
# updating the status information, inheriting from ModelForm
class StatusUpdateForm(forms.ModelForm):

    # using widgets to update the status for a course chosen through a dropdown menu
    widgets = {
        'status_update': forms.TextInput(attrs={'max_length': 255, 'placeholder': 'Enter status update'}),
        'course': forms.Select() 
    }

    # The form is linked to the Enrollment model
    # ['status_update', 'course'] are the fields to be updated
    class Meta:
        model = Enrollment  
        fields = ['status_update', 'course'] 


# Updating the teacher information, inheriting from ModelForm (similar to the student form)
class TeacherUpdateForm(forms.ModelForm):
    # street_address, post_code, city and country are the information to be updated
    # defined with attributes and widgets
    # all fields are optional, there fore the forms can be updated only with one field
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the street address'}),
        required=False
    )
    post_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the post code'}),
        required=False
    )
    city = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the city'}),
        required=False
    )
    country = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the country'}),
        required=False
    )
    
    # the form is linked to the Teacher Model
    # ['profile_picture', 'street_address', 'post_code', 'city', 'country'] are the fields to be updated
    class Meta:
        model = Teacher
        fields = ['profile_picture', 'street_address', 'post_code', 'city', 'country']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }