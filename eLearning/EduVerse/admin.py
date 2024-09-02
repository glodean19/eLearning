'''
This code registers all the models in the Django admin site
'''
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Enrollment)
admin.site.register(Message)