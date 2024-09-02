'''
The serializers convert the models into JSON data types. Some serializers call
other serializers output.

References: https://www.django-rest-framework.org/api-guide/serializers/,
https://www.geeksforgeeks.org/modelserializer-in-serializers-django-rest-framework/,
https://medium.com/@vivekpemawat/the-choice-between-serializers-modelserializer-and-serializers-serializer-django-60d11ec96904
'''

from rest_framework import serializers
from .models import *

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'user_type', 'date_of_birth']
        # Setting the password field to be write-only
        extra_kwargs = {'password': {'write_only': True}}

    # Overriding the create method to handle user creation with password hashing
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

# Serializer for the Address model
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'street_address', 'post_code', 'city', 'country', 'user']

# Serializer for the Student model
class StudentSerializer(serializers.ModelSerializer):
    # Using the UserSerializer to include user details
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['id', 'user', 'profile_picture']

# Serializer for the Teacher model (similar to StudentSerializer)
class TeacherSerializer(serializers.ModelSerializer):
    # Nesting the UserSerializer to include user details
    user = UserSerializer()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'profile_picture']

# Serializer for the Course model
class CourseSerializer(serializers.ModelSerializer):
    # Nesting the TeacherSerializer to include teacher details
    teacher = TeacherSerializer()
    # Custom field to count enrolled students
    enrolled_students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'course_start_date', 'course_length', 'midterm_deadline', 'final_deadline', 'teacher', 'enrolled_students']

    def get_enrolled_students(self, obj):
        # Custom method to get the number of enrolled students
        return obj.enrolled_student_count()

# Serializer for the Enrollment model
class EnrollmentSerializer(serializers.ModelSerializer):
    # Using the StudentSerializer and the CourseSerializer 
    # to include student and course details
    student = StudentSerializer()
    course = CourseSerializer()

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'status_update', 'enrollment_date']

# Serializer for the Feedback model
class FeedbackSerializer(serializers.ModelSerializer):
    # Using the EnrollmentSerializer to include enrollment details
    enrollment = EnrollmentSerializer()

    class Meta:
        model = Feedback
        fields = ['id', 'enrollment', 'feedback_text', 'created_at']

# Serializer for the Message model
class MessageSerializer(serializers.ModelSerializer):
    # Using the UserSerializer to include author details
    author = UserSerializer()

    class Meta:
        model = Message
        fields = ['id', 'reference_id', 'message', 'author', 'isRead', 'type', 'extraData']
