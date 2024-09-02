'''
Reference: https://simpleisbetterthancomplex.com/tutorial/2018/01/18/how-to-implement-multiple-user-types-with-django.html,
https://learndjango.com/tutorials/django-best-practices-referencing-user-model
'''

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.conf import settings

# Custom User Manager to handle user creation and superuser creation
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        # Normalize the email address
        email = self.normalize_email(email)
        # Create a new user instance
        user = self.model(email=email, **extra_fields)
        # Set the password (hashed)
        user.set_password(password)
        # Save the user to the database
        user.save(using=self._db)
        return user

    # Ensure superuser is staff and is superuser
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Create the superuser with given email and password
        return self.create_user(email, password, **extra_fields)

# Custom User model extending Django's AbstractUser
class User(AbstractUser):
    # Define user roles as choices
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    user_type = models.CharField(max_length=10, choices=ROLE_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    # Use email as the unique identifier instead of username
    email = models.EmailField(unique=True)
    # Use email to log in
    USERNAME_FIELD = 'email'
    # Additional required fields
    REQUIRED_FIELDS = ['first_name', 'last_name']
    # Use the custom manager
    objects = UserManager()  

    def save(self, *args, **kwargs):
        # Default the username to the email if not provided
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)
        # Automatically create a related Student or Teacher profile based on user type
        if self.user_type == 'student':
            Student.objects.get_or_create(user=self)
        elif self.user_type == 'teacher':
            Teacher.objects.get_or_create(user=self)
    # Return the email as the string representation of the user
    def __str__(self):
        return self.email
    # Return the user's full name
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_user'

# Address model to store user addresses
class Address(models.Model):
    street_address = models.CharField(max_length=255)
    post_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='address', default=1)
    # Return a formatted address
    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country}, {self.post_code}"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_address'

# Course model representing the course table
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    course_start_date = models.DateField()
    course_length = models.IntegerField() 
    midterm_deadline = models.DateField()
    final_deadline = models.DateField()
    # Teacher teaching the course
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name='courses_taught', default=1)
    # Students enrolled in the course
    students = models.ManyToManyField('Student', through='Enrollment', related_name='enrolled_courses', limit_choices_to={'user_type': 'student'})
    # uploaded course materials
    materials = models.FileField(upload_to='course_materials/', null=True, blank=True)
    # Return the course name as the string representation
    def __str__(self):
        return self.course_name
    # Count and return the number of enrolled students
    def enrolled_student_count(self):
        return Enrollment.objects.filter(course=self).count()
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_course'

# Student model representing a student profile
class Student(models.Model):
    # Link to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    # Profile picture with a default placeholder
    profile_picture = models.ImageField(upload_to='picture_profile/', null=True, blank=True, default='images/placeholder.png')
    # Return the full name and 'Student' as the string representation
    def __str__(self):
        return f"{self.user.get_full_name()} (Student)"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_student'

# Teacher model representing a teacher profile
class Teacher(models.Model):
    # Link to the User model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile')
    # Profile picture with a default placeholder
    profile_picture = models.ImageField(upload_to='picture_profile/', null=True, blank=True, default='images/placeholder.png')
    # Return the full name and 'Teacher' as the string representation
    def __str__(self):
        return f"{self.user.get_full_name()} (Teacher)"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_teacher'

# Enrollment model representing a student's enrollment in a course
class Enrollment(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    status_update = models.TextField(blank=True)
    # Timestamp of when the enrollment was created
    enrollment_date = models.DateTimeField(auto_now_add=True)
    # Return a string representation of the enrollment
    def __str__(self):
        return f"{self.student.user.get_full_name()} enrolled in {self.course.course_name}"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_enrollment'
        unique_together = ('student', 'course')

# Feedback model for collecting feedback related to enrollments
class Feedback(models.Model):
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    # Timestamp of when the feedback was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Return a string representation of the feedback
    def __str__(self):
        return f"Feedback for {self.enrollment.course.course_name} by {self.enrollment.student.user.get_full_name()}"
    # Specify the database table name
    class Meta:
        db_table = 'EduVerse_feedback'

# Message model for storing messages sent and received in the chat room
class Message(models.Model):
    reference_id = models.CharField(max_length=100)
    message = models.TextField()
    # Link to User model
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  
    isRead = models.BooleanField(default=False)
    type = models.IntegerField()
    extraData = models.TextField()
    # Return the message content as the string representation
    def __str__(self):
        return self.message