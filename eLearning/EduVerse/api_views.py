'''
Class views to fetch all objects from the database (queryset),
defines which serializer should be used to convert the model instances to and from JSON format,
set the permissions required to access the actions.
Perform_create customises the create action.

Reference: https://www.django-rest-framework.org/api-guide/viewsets/ and 
https://www.django-rest-framework.org/api-guide/generic-views/
'''

from rest_framework import viewsets, permissions
from .serializers import *
from .models import *

class UserViewSet(viewsets.ModelViewSet):
    # Queryset containing all User objects
    queryset = User.objects.all()
    # Serializer class to convert User instances to/from JSON
    serializer_class = UserSerializer
    # Only admin users can manage users
    permission_classes = [permissions.IsAdminUser]  

class AddressViewSet(viewsets.ModelViewSet):
    # Queryset containing all Address objects
    queryset = Address.objects.all()
    # Serializer class to convert Address instances to/from JSON
    serializer_class = AddressSerializer
    # Users must be authenticated
    permission_classes = [permissions.IsAuthenticated]  

class StudentViewSet(viewsets.ModelViewSet):
    # Queryset containing all Student objects
    queryset = Student.objects.all()
    # Serializer class to convert Stuident instances to/from JSON
    serializer_class = StudentSerializer
    # Only authenticated users can access student profiles
    permission_classes = [permissions.IsAuthenticated]  

class TeacherViewSet(viewsets.ModelViewSet):
    # Queryset containing all Teacher objects
    queryset = Teacher.objects.all()
    # Serializer class to convert Teacher instances to/from JSON
    serializer_class = TeacherSerializer
    # Only authenticated users can access teacher profiles
    permission_classes = [permissions.IsAuthenticated]  

class CourseViewSet(viewsets.ModelViewSet):
    # Queryset containing all Course objects
    queryset = Course.objects.all()
    # Serializer class to convert Course instances to/from JSON
    serializer_class = CourseSerializer
    # Only authenticated users can access the courses
    permission_classes = [permissions.IsAuthenticated]

    # Overriding the default create behavior to ensure that only teachers can create courses
    def perform_create(self, serializer):
        if self.request.user.user_type == 'teacher':
            # Save the course with the teacher linked to the current authenticated user
            serializer.save(teacher=self.request.user.teacher_profile)
        else:
             # Raise a permission error if the user is not a teacher
            raise permissions.PermissionDenied("Only teachers can create courses.")

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    # Serializer class to convert Enrollment instances to/from JSON
    serializer_class = EnrollmentSerializer
    # Only authenticated users can access the enrollment
    permission_classes = [permissions.IsAuthenticated]

    # Overriding the default create behavior to link enrollment to the authenticated student
    def perform_create(self, serializer):
        if self.request.user.user_type == 'student':
            # Save the enrollment with the student linked to the current authenticated user
            student = self.request.user.student_profile
            serializer.save(student=student)
        else:
            # Raise a permission error if the user is not a student
            raise permissions.PermissionDenied("Only students can enroll in courses.")

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    # Serializer class to convert Feedback instances to/from JSON
    serializer_class = FeedbackSerializer
    # Only authenticated users can access the feedback
    permission_classes = [permissions.IsAuthenticated]

    # Overriding the default create behavior to link feedback to the corresponding enrollment
    def perform_create(self, serializer):
        enrollment = Enrollment.objects.get(
            # Ensure the enrollment belongs to the current student
            student=self.request.user.student_profile,
            # Match the course in the feedback
            course=serializer.validated_data['enrollment'].course
        )
        # Save the feedback with the enrollment
        serializer.save(enrollment=enrollment)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    # Serializer class to convert Message instances to/from JSON
    serializer_class = MessageSerializer
    # Only authenticated users can access the message
    permission_classes = [permissions.IsAuthenticated]

    # Overriding the default create behavior to set the author of the message as the current authenticated user
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
