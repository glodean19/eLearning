'''
The method 'user_login' handles the validation process of the login, where it retrieves and authenticate email and password
and based on the user type, it redirects to the appropriate page.
Reference: https://stackoverflow.com/questions/75401759/how-to-set-up-login-view-in-python-django,
https://openclassrooms.com/en/courses/7107341-intermediate-django/7263317-create-a-login-page-with-a-function-based-view,

The method 'user_logout' invalidates the user session, removing every data and redirecting the user to the home page.
Reference: https://www.codeswithpankaj.com/post/create-a-login-logout-system-in-django-step-by-step-instructions,
https://pylessons.com/django-login-logout

The method 'registration' manages the user registration process. When the registration form is submitted, 
it validates and saves the new user, encrypts the password, and creates an associated address and user profile (either student or teacher). 
If the registration is successful, the user is redirected to the homepage. 
Reference: https://gghantiwala.medium.com/django-restricting-pages-and-creating-a-registration-form-cfb124d1fe0a,
https://reintech.io/blog/working-with-forms-in-django-tutorial-for-software-developers

The method 'student_home' displays the relevant information of the logged-in student, such as:
the courses in which the student is enrolled, all available courses and status update. 
Students can also update their profile information using a form provided on the page.

The method 'teacher_home' displays all courses thaught by the logged-in teacher.
it also allows them to search for users, updating them or adding new courses, and update their profile information. 

Refrence (student and teacher): https://docs.djangoproject.com/en/5.1/topics/db/queries/,
https://docs.djangoproject.com/en/5.1/topics/db/managers/,
https://docs.djangoproject.com/en/5.1/ref/templates/api/#playing-with-context,
https://docs.djangoproject.com/en/5.1/topics/http/shortcuts/,
https://djangocentral.com/capturing-query-parameters-of-requestget-in-django/,
https://books.agiliq.com/projects/django-orm-cookbook/en/latest/query_relatedtool.html,
https://stackoverflow.com/questions/70001213/django-queryset-searching-for-firstname-and-lastname-with-startswith,
https://www.fafadiatech.com/blog/summary-django-i-didnt-know-queryset-could-do-that/

The method 'course_home' provides an overview of a specific course when the student is logged-in, 
including a list of enrolled students and any feedback. 
Reference: https://stackoverflow.com/questions/51529018/django-messages-success-message-with-data-from-submitted-form,

The method 'course_detail' allows teachers to view and edit the details of a specific course they teach. 
It displays the course's feedback, start date, deadlines, and other information. 
Reference: https://stackoverflow.com/questions/69263191/why-do-i-need-to-specify-html-file-in-render

The method 'new_course' helps the teachers to create a new course, through a form where the teacher can input the course details. 
When the form is submitted and validated, the course is saved and associated with the teacher who created it. 
Reference: https://forum.djangoproject.com/t/how-to-enroll-students-into-a-course/21581

The method 'room' sets up the chat room for a specific course. It retrieves the course by name and generates a unique session reference
for the logged-in user. 
Reference: https://www.geeksforgeeks.org/generating-random-ids-using-uuid-python/


The methods 'store_info' and 'get_info' are used to store the room_id under a key in Redis and retrieve it. This has been used to
pass the room_id from the student initiating the chat to the teacher and create the ws/chat/roomId Websocket.
Reference: https://redis.io/docs/latest/develop/get-started/data-store/,
https://redis-py2.readthedocs.io/en/latest/
'''

from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import uuid
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import redis
from django.urls import reverse
from .models import *
from django.db.models import Q
from django.db import IntegrityError
from .forms import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


# Render the homepage template
def index(request):
    return render(request, 'index.html')


# This view handles the login to the app from an existing user
def user_login(request):
    # if received the POST request, get the email and password and autheticate them
    if request.method == 'POST':
        email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        # if the user exists, login in the app
        if user is not None:
            login(request, user)

            # Set session data for the logged-in user
            request.session['user_id'] = user.id
            request.session['user_type'] = user.user_type
            request.session['reference'] = str(uuid.uuid4())
            
            # if the user is a student, it redirects to the student home
            if user.user_type == 'student':
                student = get_object_or_404(Student, user=user)
                request.session['student_id'] = student.pk
                return redirect('student_home', pk=student.pk)
            # if the user is a teacher, it redirects to the teacher home
            elif user.user_type == 'teacher':
                teacher = get_object_or_404(Teacher, user=user)
                request.session['teacher_id'] = teacher.pk
                return redirect('teacher_home', pk=teacher.pk)
            # otherwise it displays an error message
        else:
            messages.error(request, 'Invalid email or password.')
    # renders the home page
    return render(request, 'index.html')

# when the user click on the logout, it redirects to the home page
def user_logout(request):
    logout(request)
    return redirect('index') 

# this view handles the registration of a new user
def registration(request):
    # if a POST request is received
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        # it checks if the form submitted is valid
        if form.is_valid():
            try:
                # Save user without committing to the database yet
                user = form.save(commit=False)
                # Hash the password
                user.set_password(form.cleaned_data['password'])
                user.save()
                
                # Save the address associated with the user
                address = Address(
                    street_address=form.cleaned_data['street_address'],
                    post_code=form.cleaned_data['post_code'],
                    city=form.cleaned_data['city'],
                    country=form.cleaned_data['country'],
                    user=user
                )
                address.save()

                # Create the Student or Teacher profile if it doesn't already exist
                if user.user_type == 'student':
                    Student.objects.get_or_create(
                        user=user,
                        defaults={'address': address, 'profile_picture': 'images/placeholder.png'} 
                    )
                elif user.user_type == 'teacher':
                    Teacher.objects.get_or_create(
                        user=user,
                        defaults={'address': address, 'profile_picture': 'images/placeholder.png'} 
                    )
                
                # Redirect to the home page
                return redirect('index')  
            
            # it checks if the user already exist
            except IntegrityError:
                form.add_error(None, 'A profile for this user already exists.')

    else:
        # Create a new blank form
        form = RegistrationForm()  
    # Render the registration page
    return render(request, 'registration.html', {'form': form})

# this view handles the student home
def student_home(request, pk):
    # Fetch the student based on the primary key
    student = get_object_or_404(Student, pk=pk)
    
    # Fetch all the courses the student is currently enrolled in
    enrolled_courses = Course.objects.filter(students=student)

    # Fetch all available courses
    available_courses = Course.objects.all()

    # Fetch enrollments for the student to get the status updates
    enrollments = Enrollment.objects.filter(student=student).order_by('-enrollment_date')

    if request.method == 'POST':
        # Handle posting a new status update
        if 'status_update' in request.POST:   
            status_update = request.POST.get('status_update')
            course_id = request.POST.get('course')
            course = Course.objects.get(pk=course_id)
            enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)
            enrollment.status_update = status_update
            enrollment.save()
            # Set the form after saving the status update
            form = StudentUpdateForm(instance=student)
        else:
            # Handle updating student details
            form = StudentUpdateForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                # Save the student details
                student = form.save(commit=False)
                
                # Handle address updates
                user = student.user
                address = user.address

                # Get the list of fields that have changed in the form
                changed_fields = form.changed_data

                # if any of the address-related fields (street_address, post_code, city, country) are included in the form submission and 
                # have new values, those changes are applied to the existing address record.
                if 'street_address' in changed_fields:
                    address.street_address = form.cleaned_data.get('street_address', address.street_address)
                if 'post_code' in changed_fields:
                    address.post_code = form.cleaned_data.get('post_code', address.post_code)
                if 'city' in changed_fields:
                    address.city = form.cleaned_data.get('city', address.city)
                if 'country' in changed_fields:
                    address.country = form.cleaned_data.get('country', address.country)

                address.save()
                student.save()
                return redirect('student_home', pk=pk)
            else:
                print("Form errors:", form.errors)
    else:
        # Initialize the form if not a POST request
        form = StudentUpdateForm(instance=student)

    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'enrollments': enrollments,
        'form': form,
        'available_courses': available_courses,
    }

    return render(request, 'student.html', context)

# this view handles how the student see a course page
def course_home(request, pk):
    # Fetch the course based on the primary key (pk)
    course = get_object_or_404(Course, pk=pk)
    
    # Get all students enrolled in the course
    enrolled_students = course.students.all()

    # Fetch the student based on the currently logged-in user
    student = get_object_or_404(Student, user=request.user)
    
    # Check if the student is enrolled in the course
    is_enrolled = student and course in student.enrolled_courses.all() if student else False

    if request.method == 'POST':
        # Handle feedback submission
        feedback_text = request.POST.get('feedback')
        if student and feedback_text:
            # Fetch the existing enrollment for the student and course
            enrollment = Enrollment.objects.get(student=student, course=course)
            # Create a new Feedback record
            Feedback.objects.create(enrollment=enrollment, feedback_text=feedback_text)
            # Redirect to the same course page after feedback is saved
            return redirect(reverse('course_home', kwargs={'pk': pk}))

        # Handle course enrollment
        if 'enroll' in request.POST:
            if not is_enrolled:
                # Create a new Enrollment record for the student and course
                Enrollment.objects.create(student=student, course=course)

                # Send a message to the teacher's WebSocket connection
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"teacher_{course.teacher.id}",
                    {
                        'type': 'student_enrolled',
                        'student_name': f"{student.user.first_name} {student.user.last_name}",
                        'course_name': course.course_name,
                        'enrolled_student_count': course.students.count() + 1,
                        'course_id': course.pk, 
                    }
                )
                # Show a success message to the user
                messages.success(request, 'You have been enrolled in the course.')
                # Redirect to the same course page after enrollment
                return redirect(reverse('course_home', kwargs={'pk': pk}))
            else:
                # Inform the user if they are already enrolled
                messages.info(request, 'You are already enrolled in this course.')

    # Fetch all feedback related to the course
    feedbacks = Feedback.objects.filter(enrollment__course=course)
    
    # Prepare the context data for rendering the template
    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'student': student,
        'is_enrolled': is_enrolled,
        'feedbacks': feedbacks,
        'materials': course.materials,
    }
    
    # Render the course page template with the context data
    return render(request, 'course.html', context)


# this view handles the teacher home
def teacher_home(request, pk):
    # Fetch the teacher based on the primary key
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher_full_name = request.user.get_full_name()
    # when the form is received and it's valid
    if request.method == 'POST':
        form = TeacherUpdateForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            # Save the teacher details
            teacher = form.save(commit=False)
            
            # update address 
            user = teacher.user
            address = user.address

            # Only update address if any address fields are provided, to avoid updating to empty fields
            if any(form.cleaned_data.get(field) for field in ['street_address', 'post_code', 'city', 'country']):
                address.street_address = form.cleaned_data.get('street_address', address.street_address)
                address.post_code = form.cleaned_data.get('post_code', address.post_code)
                address.city = form.cleaned_data.get('city', address.city)
                address.country = form.cleaned_data.get('country', address.country)
                address.save()

            # Save the teacher object (including profile picture if provided, like for the student)
            teacher.save()

            # Redirect to the updated teacher home page
            return redirect('teacher_home', pk=pk)
    else:
        # Prepopulate the form with teacher data
        form = TeacherUpdateForm(instance=teacher)
    # Get all courses taught by the teacher
    courses = teacher.courses_taught.all()
    course_names = [course.course_name for course in courses]
    # this handles the query in search bar and initialize an empty queryset for search results
    query = request.GET.get('q', '')
    results = User.objects.none()
    # if there is a query in the search bar, it performs the search based on the query
    if query:
        results = User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query.split(' ')[0]) & Q(last_name__icontains=query.split(' ')[-1])
        )

    # create a unique reference for the session
    reference = str(uuid.uuid4()) 

    context = {
        'teacher': teacher,
        'courses': courses,
        'reference': reference,
        'form': form,
        'query': query,
        'results': results,
        'user_type': 'teacher',
        'author': teacher_full_name,
        'course_names': course_names,
    }
    
    return render(request, 'teacher.html', context)

# the teacher can update the detail of a course taught
def course_detail(request, pk):
    # Fetch the course based on the primary key (pk)
    course = get_object_or_404(Course, pk=pk)
    
    # Fetch all feedbacks associated with the course
    feedbacks = Feedback.objects.filter(enrollment__course=course)
    
    # Fetch the teacher associated with the current logged-in user
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Fetch all students enrolled in the course
    enrolled_students = Enrollment.objects.filter(course=course).select_related('student')

    if request.method == 'POST':
        # Handle removing a student from the course
        if 'remove_student' in request.POST:
            student_pk = request.POST.get('student_pk')

            try:
                # Retrieve the enrollment record for the student and course
                enrollment = Enrollment.objects.get(course_id=pk, student_id=student_pk)
                # Delete the enrollment record
                enrollment.delete()

                # Get the channel layer for WebSocket communication
                channel_layer = get_channel_layer()
                # Define the group name for notifying student removal
                student_removed_group_name = f"student_{student_pk}"

                # Send a message to the student's WebSocket group about removal
                async_to_sync(channel_layer.group_send)(
                    student_removed_group_name,
                    {
                        'type': 'student_removed',
                        'student_id': student_pk,
                        'course_id': pk
                    }
                )

                # Redirect back to the course detail page
                return redirect(reverse('course_detail', args=[pk]))

            except Enrollment.DoesNotExist:
                # If the enrollment does not exist, redirect back to the course detail page
                return redirect(reverse('course_detail', args=[pk]))

        else:
            # Handle updating course details
            course.course_name = request.POST.get('course_name')
            course.course_start_date = request.POST.get('course_start_date')
            course.course_length = request.POST.get('course_length')
            course.midterm_deadline = request.POST.get('midterm_deadline')
            course.final_deadline = request.POST.get('final_deadline')

            # Check if new materials are uploaded
            if 'materials' in request.FILES:
                course.materials = request.FILES['materials']

                # Save the updated course details
                course.save()

                # Notify the course group about the material update
                channel_layer = get_channel_layer()
                course_group_name = f'course_{course.pk}'

                async_to_sync(channel_layer.group_send)(
                    course_group_name,
                    {
                        'type': 'update_material',
                        'course_name': course.course_name,
                        'course_id': course.pk
                    }
                )

                # Notify all enrolled students about the material update
                for enrollment in enrolled_students:
                    student = enrollment.student
                    student_group_name = f'student_{student.id}'
                    
                    async_to_sync(channel_layer.group_send)(
                        student_group_name,
                        {
                            'type': 'update_material',
                            'course_name': course.course_name,
                            'course_id': course.pk
                        }
                    )

                # Show a success message to the user
                messages.success(request, 'Materials uploaded and course updated successfully.')

    # Render the course detail template with context data
    return render(request, 'course_detail.html', {
        'course': course,
        'feedbacks': feedbacks,
        'teacher': teacher,
        'enrolled_students': enrolled_students,
    })


# this view is for the teacher to create new courses
def new_course(request, pk):
    # Fetch teacher by primary key
    teacher = get_object_or_404(Teacher, pk=pk)  
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            # Create a course instance
            course = form.save(commit=False)  
            # Associate the course with the teacher
            course.teacher = teacher 
            # Save the course instance 
            course.save()  
            # redirects to the teacher home
            return redirect(reverse('teacher_home', kwargs={'pk': teacher.pk}))
    else:
        # this part render a blank course form to add new courses
        form = CourseForm()
    return render(request, 'new_course.html', {'form': form})

# this view handles the chat room
def room(request, course_name):
    # Get course based on course_name
    course = get_object_or_404(Course, course_name=course_name)
    
    # Get user details
    student_full_name = request.user.get_full_name()
    # create a unique reference for the session
    reference = str(uuid.uuid4())
    
    context = {
        'course': course,
        'reference': reference,
        'author': student_full_name,  
        'room_id': course.pk,
        'user_type': 'student',
        'course_name': course.course_name,
    }
    return render(request, 'room.html', context)

# Initialize a Redis client to connect to a Redis server running on localhost
# The Redis server is assumed to be running on the default port 6379 and using database 0
# different than using Redis for setting the Django Channels like shown in the settings
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

@csrf_exempt
def store_info(request):
    # This view function is responsible for storing data in Redis
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Extract 'room_id' from the parsed JSON data
            room_id = data.get('room_id')
            
            # Store the 'room_id' value in Redis with the key 'room_id'
            redis_client.set('room_id', room_id)
            
            # Return a JSON response indicating success and echo the room_id
            return JsonResponse({'status': 'success', 'room_id': room_id})
        except json.JSONDecodeError:
            # Return a 400 Bad Request response if JSON decoding fails
            return HttpResponseBadRequest('Invalid JSON')

def get_info(request):
    # This view function is responsible for retrieving data from Redis
    if request.method == 'GET':
        # Retrieve the value associated with the key 'room_id' from Redis
        room_id = redis_client.get('room_id')
        
        if room_id:
            # Return the room_id as a JSON response, decoding from bytes to a string
            return JsonResponse({
                'room_id': room_id.decode('utf-8'),
            })
        else:
            # Return a 404 Not Found response if the room_id is not found in Redis
            return JsonResponse({'error': 'Room ID not found'}, status=404)


