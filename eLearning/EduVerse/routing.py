'''
The URL chat captures the room_id and 
converts the ChatConsumer class into an ASGI application,
required for handling WebSocket connections.

The following two URL (remove-student and notification-changes) capture both
the context type and context ID and convert the RemoveStudentConsumer and NotificationConsumer 
classes into the ASGI applications.

Reference: https://forum.djangoproject.com/t/websocket-connection-to-django-channels/28824
'''

from django.urls import re_path
from . import consumers

# Defining the URL patterns for the WebSocket connections
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/remove-student/(?P<context_type>\w+)/(?P<context_id>\d+)/$', consumers.RemoveStudentConsumer.as_asgi()),
    re_path(r'ws/notifications-change/(?P<context_type>\w+)/(?P<context_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]
