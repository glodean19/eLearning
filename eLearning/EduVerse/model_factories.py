'''
Each factory corresponds to the Django model and it creates 
instances of that model with predefined or randomly generated data.

Sequence: unique values in a specific format
Faker: realistic, random values
SubFactory: associations with another factory
LazyAttribute: It takes as argument a method to call (usually a lambda). The method is a sole argument

Reference:https://factoryboy.readthedocs.io/en/stable/orms.html,
https://factoryboy.readthedocs.io/en/stable/recipes.html,
https://www.hacksoft.io/blog/improve-your-tests-django-fakes-and-factories-advanced-usage
'''

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import *

# Getting the custom User model
User = get_user_model()

# Factory class for generating User model instances
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    # Generating sequential fields and using lambdas for dynamic values
    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: 'user{}'.format(n))
    email = factory.Sequence(lambda n: 'user{}@example.com'.format(n))
    first_name = factory.Sequence(lambda n: f'First{n}')
    last_name = factory.Sequence(lambda n: f'Last{n}')
    # Password hashed with a default value
    password = factory.LazyFunction(lambda: make_password('password123'))
    # Randomly picks between 'student' or 'teacher'
    user_type = factory.Iterator(['student', 'teacher'])

# Factory class for generating Address model instances
class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    # Using Faker to generate realistic fake data
    street_address = factory.Faker('street_address')
    post_code = factory.Faker('postcode')
    city = factory.Faker('city')
    country = factory.Faker('country')
    # Creates a related User instance using the UserFactory
    user = factory.SubFactory(UserFactory)

# Factory class for generating Teacher model instances
class TeacherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Teacher

    # Ensures the user_type is set to 'teacher'
    user = factory.SubFactory(UserFactory, user_type='teacher')
    # Generates an image with a blue color
    profile_picture = factory.django.ImageField(color='blue')

# Factory class for generating Student model instances (similar to TeacherFactory)
class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    # Creates a related User instance using the UserFactory
    user = factory.SubFactory(UserFactory)
    # Generates an image with a red color
    profile_picture = factory.django.ImageField(color='red')

# Factory class for generating Course model instances
class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    course_name = factory.Faker('sentence', nb_words=4)
    course_start_date = factory.Faker('date_this_year')
    course_length = factory.Faker('random_int', min=4, max=12)
    midterm_deadline = factory.Faker('date_this_year')
    final_deadline = factory.Faker('date_this_year')
    # Creates a related Teacher instance using the TeacherFactory
    teacher = factory.SubFactory(TeacherFactory)

# Factory class for generating Enrollment model instances
class EnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Enrollment

    # Creates a related Student instance using the StudentFactory
    student = factory.SubFactory(StudentFactory)
    # Creates a related Course instance using the CourseFactory
    course = factory.SubFactory(CourseFactory)
    status_update = factory.Faker('text')
    # Sets the enrollment date to the current time
    enrollment_date = factory.LazyAttribute(lambda o: timezone.now())

# Factory class for generating Feedback model instances
class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feedback

    # Creates a related Enrollment instance using the EnrollmentFactory
    enrollment = factory.SubFactory(EnrollmentFactory)
    feedback_text = factory.Faker('text')
    # Sets the creation time to the current time
    created_at = factory.LazyAttribute(lambda o: timezone.now())

# Factory class for generating Message model instances
class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    reference_id = factory.Faker('uuid4')
    message = factory.Faker('text')
    author = factory.SubFactory(UserFactory)
    isRead = factory.Faker('boolean')
    type = factory.Faker('random_int', min=0, max=10)
    extraData = factory.Faker('text')
