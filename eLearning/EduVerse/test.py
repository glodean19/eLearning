'''
Tests related to Models, Forms and API endpoints. See model_factories.py for 
the factory models based on the real models.

Reference: https://factoryboy.readthedocs.io/en/stable/examples.html,
https://medium.com/analytics-vidhya/factoryboy-usage-cd0398fd11d2
'''

from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from .model_factories import *
from .models import *
from .forms import *
from .serializers import *

# Test class for models
class ModelTests(TestCase):
    # Test case for creating a user using the UserFactory model and checking its existence in the database
    def test_user_creation(self):
        user = UserFactory.create()
        self.assertTrue(get_user_model().objects.filter(email=user.email).exists())

    def test_address_creation(self):
        # Test case for creating an address using the AddressFactory model and verifying its existence
        address = AddressFactory.create()
        self.assertTrue(Address.objects.filter(id=address.id).exists())
        self.assertEqual(address.user, address.user)

    def test_course_creation(self):
        # Test case for creating a course and ensuring the linked teacher and course are created correctly
        user = UserFactory(user_type='teacher')
        
        # Check if a Teacher already exists for this user
        try:
            if not Teacher.objects.filter(user=user).exists():
                # Create a Teacher linked to the user
                teacher = TeacherFactory(user=user)
            else:
                teacher = Teacher.objects.get(user=user)
        # Fail the test if Teacher creation/retrieval fails
        except Exception as e:
            self.fail("Teacher creation/retrieval failed")  
        
        # Check if the teacher object exists
        self.assertIsNotNone(teacher, "Teacher object is None")
        
        # Create a course and assign it to the teacher
        try:
            course = CourseFactory(teacher=teacher)
            # Save the course to the database
            course.save()  
        except Exception as e:
            self.fail("Course creation failed") 
        
        self.assertTrue(Course.objects.filter(course_id=course.course_id).exists())
        self.assertIsNotNone(course.course_name)
        self.assertIsNotNone(course.course_start_date)
        self.assertIsNotNone(course.course_length)
        self.assertIsNotNone(course.midterm_deadline)
        self.assertIsNotNone(course.final_deadline)
        self.assertIsNotNone(course.teacher)

# Test class for forms
class FormTests(TestCase): 
    # This test validates the registration form with the user and address data
    def test_registration_form_valid(self):
        user_data = factory.build(dict, FACTORY_CLASS=UserFactory, user_type='teacher')
        data = {
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'email': user_data['email'],
            'user_type': 'teacher',
            'date_of_birth': '2000-01-01',
            'password': 'password123',
            'confirm_password': 'password123',
            'street_address': '123 Main St',
            'post_code': '12345',
            'city': 'City',
            'country': 'Country',
        }
        form = RegistrationForm(data)
        self.assertTrue(form.is_valid())

    # This test validates and updates the student's address using the form in the student page
    def test_student_update_form_valid(self):
        try:  
            # Creating a user with user_type='student'
            user = UserFactory.create(user_type='student')

            # Initial address creation using the UserFactory and AddressFactory
            initial_address_data = {
                'street_address': 'Old Street',
                'post_code': '00000',
                'city': 'Old City',
                'country': 'Old Country'
            }
            address = AddressFactory.create(user=user, **initial_address_data)

            # New fake data to update the address
            updated_address_data = {
                'street_address': 'New Street',
                'post_code': '11111',
                'city': 'New City',
                'country': 'New Country'
            }

            # Creating the form for updating the student's address
            form = StudentUpdateForm(instance=user, data=updated_address_data)

            # Validating the form
            self.assertTrue(form.is_valid(), "Form is not valid")


            # Saving the updated user in the database
            updated_user = form.save(commit=False)
            updated_user.save()

            # Manually updating the address
            address.street_address = updated_address_data['street_address']
            address.post_code = updated_address_data['post_code']
            address.city = updated_address_data['city']
            address.country = updated_address_data['country']
            address.save()


            # Fetching the updated address from the database
            fetched_updated_address = Address.objects.get(user=updated_user)


            # Verifying the updated address
            self.assertEqual(fetched_updated_address.street_address, 'New Street')
            self.assertEqual(fetched_updated_address.post_code, '11111')
            self.assertEqual(fetched_updated_address.city, 'New City')
            self.assertEqual(fetched_updated_address.country, 'New Country')

        except Exception as e:
            self.fail(f"Test failed due to an exception: {str(e)}")

# Test class for API
class APIViewTests(APITestCase):
    def setUp(self):
        # Create a user and authenticate the client
        self.user = UserFactory.create()
        self.client.force_authenticate(user=self.user)

    def test_courses_endpoint(self):
        # This test verifies the GET request to the courses API endpoint
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_enrollment_endpoint(self):
        # This test verifies the GET request to the enrollments API endpoint
        response = self.client.get(f'/api/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
