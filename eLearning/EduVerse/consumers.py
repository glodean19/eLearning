'''
These classes allow handling the WebSocket connections asynchronously.
Each class calls methods for the client to connect and disconnect to a websocket,
send and receive the messages about the author, message type, course name and so on.

Reference: https://channels.readthedocs.io/en/stable/tutorial/part_3.html,
https://medium.com/atomic-loops/django-channels-is-all-you-need-94628dd6815c,
https://github.com/twtrubiks/django-channels2-tutorial/blob/master/chat/consumers.py
'''

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import *
import logging

logger = logging.getLogger('EduVerse.NotificationConsumer')


User = get_user_model()

# Class chat for asynchronous websocket
class ChatConsumer(AsyncWebsocketConsumer):

    # Asynchronously called when the WebSocket connection is opened
    async def connect(self):
        # Extract room ID from the URL route and set the room group name
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'  # Group name for the chat room

        # Add the current channel to the group associated with the room_id
        await self.channel_layer.group_add(
            self.room_group_name, 
            self.channel_name      
        )
        # Accept the WebSocket connection
        await self.accept()

    # Asynchronously called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        # Remove the current channel from the group
        await self.channel_layer.group_discard(
            self.room_group_name, 
            self.channel_name     
        )

    # Asynchronously called when a message is received from the WebSocket
    async def receive(self, text_data):
        # Parse the JSON data received from WebSocket and 
        # determine the type of message received
        data = json.loads(text_data)
        message_type = data.get('type')  

        # Extract course name from the data if provided
        course_name = data.get('course_name', '')
        if course_name:
            # Send the course name to the group, 
            # which will be handled by the 'course_name' handler
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'course_name',   
                    'course_name': course_name,  
                }
            )

        # If the received message is not of type 'course_name', 
        # treat it as a normal chat message
        if message_type != 'course_name':
            message = data.get('message', '')  
            author = data.get('author', 'System')  

            # Send the chat message to the group, 
            # which will be handled by the 'chat_message' handler
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',  
                    'message': message,    
                    'author': author,    
                }
            )

    # Handler for chat messages sent to the group
    async def chat_message(self, event):
        # Send the chat message, author and course name (if available) to the WebSocket
        await self.send(text_data=json.dumps({
            'message': event.get('message', ''), 
            'author': event.get('author', ''),  
            'course_name': event.get('course_name', ''), 
        }))

    # Handler for course name messages sent to the group
    async def course_name(self, event):
        # Extract the course name from the event data
        course_name = event['course_name']
        # Send the course name to the WebSocket
        await self.send(text_data=json.dumps({
            'course_name': course_name, 
        }))



# Class remove student for asynchronous websocket
class RemoveStudentConsumer(AsyncWebsocketConsumer):

    # Asynchronously called when the WebSocket connection is opened
    async def connect(self):
        # Extract context ID and type from the URL route
        self.context_id = self.scope['url_route']['kwargs'].get('context_id') 
        self.context_type = self.scope['url_route']['kwargs'].get('context_type')

        # Define the group name based on the extracted context type and ID
        self.group_name = f'{self.context_type}_{self.context_id}'

        # Add the current channel to the group associated with the context
        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    # Asynchronously called when the WebSocket connection is closed
    async def disconnect(self, close_code):
        # Remove the current channel from the group
        await self.channel_layer.group_discard(
            self.group_name, 
            self.channel_name)

    # Asynchronously called when a message is received from the WebSocket
    async def receive(self, text_data):
        # Parse the JSON data received from WebSocket and 
        # determine the type of message received
        data = json.loads(text_data)
        message_type = data.get('type') 

        # Check if the message type is 'remove_student' and
        # extract the student_id and course_id
        if message_type == 'remove_student':
            student_id = data.get('student_id')
            course_id = data.get('course_id')

            # Check if both student_id and course_id are provided
            if student_id and course_id:
                # Send a message to the group indicating a student removal
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'student_removed', 
                        'student_id': student_id, 
                        'course_id': course_id   
                    }
                )
            else:
                # invalid data
                logger.warning(f"Invalid data for remove_student: {data}")

        else:
            # unexpected message type
            logger.warning(f"Unexpected message type: {message_type}")

    # Handler for student removed messages
    async def student_removed(self, event):
        # Send the student removal details to the WebSocket
        await self.send(text_data=json.dumps({
            'type': 'student_removed',        
            'student_id': event.get('student_id'), 
            'course_id': event.get('course_id')   
        }))

# Class notifications for asynchronous websocket
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Extract context ID and type from URL
        self.context_id = self.scope['url_route']['kwargs'].get('context_id')
        self.context_type = self.scope['url_route']['kwargs'].get('context_type')
        
        # Define the group name based on context
        self.group_name = f'{self.context_type}_{self.context_id}'
        
        # Join the appropriate group
        await self.channel_layer.group_add(
            self.group_name, 
            self.channel_name)
        
        await self.accept()


    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # This method is called when a message is received from the WebSocket
    async def receive(self, text_data):
        # Parse the JSON data received from WebSocket and 
        # determine the type of message received
        data = json.loads(text_data)
        message_type = data.get('type')

         # If the message type is 'student_enrolled'
        if message_type == 'student_enrolled':
            # Extract details of the enrolled student and the course
            student_name = data.get('student_name')
            course_name = data.get('course_name')
            enrolled_student_count = data.get('enrolled_student_count')
            course_id = data.get('course_id')

            # Send a message to the group indicating a student has been enrolled
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'student_enrolled',
                    'student_name': student_name,
                    'course_name': course_name,
                    'enrolled_student_count': enrolled_student_count,
                    'course_id': course_id,
                }
            )

        # If the message type is 'update_material'
        if message_type == 'update_material':
            # Extract the course name from the message
            course_name = data.get('course_name')

            # Send a message to the group indicating course materials have been updated
            await self.channel_layer.group_send(
            self.group_name, 
            {
                'type': 'update_material',
                'course_name': data.get('course_name'),
                'course_id': data.get('course_id'),
            }
            )

        else:
            # message type is not supported
            logger.warning(f"Unsupported message type in NotificationConsumer: {message_type}")

    # This method is a handler for 'update_material' messages sent to the group
    async def update_material(self, event):
        # Send the update material details back to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'update_material',
            'course_name': event.get('course_name'),
            'course_id': event.get('course_id')
        }))


    # This method is a handler for 'student_enrolled' messages sent to the group
    async def student_enrolled(self, event):
        # Send the student enrollment details back to the WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'student_enrolled',
            'student_name': event.get('student_name', 'Unknown'),
            'course_name': event.get('course_name', 'Unknown'),
            'enrolled_student_count': event.get('enrolled_student_count', 0),
            'course_id': event.get('course_id', 0),
        }))