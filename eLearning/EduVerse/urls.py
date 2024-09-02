'''
List of URLs that map to specific views in the 
views.py and api_views.py 
'''

from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from . import api_views

# Creating a DefaultRouter instance to handle API routing
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'addresses', api_views.AddressViewSet)
router.register(r'students', api_views.StudentViewSet)
router.register(r'teachers', api_views.TeacherViewSet)
router.register(r'courses', api_views.CourseViewSet)
router.register(r'enrollments', api_views.EnrollmentViewSet)
router.register(r'feedbacks', api_views.FeedbackViewSet)
router.register(r'messages', api_views.MessageViewSet)

# Defining URL patterns for the application
urlpatterns = [
    path('', views.user_login, name='index'),
    path('logout/', views.user_logout, name='logout'), 
    path('registration/', views.registration, name='registration'),
    path('student/<int:pk>/', views.student_home, name='student_home'),
    path('course/<int:pk>/', views.course_home, name='course_home'),
    path('course/<int:pk>/detail/', views.course_detail, name='course_detail'),
    path('teacher/<int:pk>/', views.teacher_home, name='teacher_home'),
    path('new_course/<int:pk>/', views.new_course, name='new_course'),
    path('chat/<str:course_name>/', views.room, name='room'),
    path('store_info/', views.store_info, name='store_info'),
    path('get_info/', views.get_info, name='get_info'),
    path('api/', include(router.urls)),
]
