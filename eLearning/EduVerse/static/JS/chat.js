/** 
 * When the DOM is fully loaded, it retrieves the user_type, room ID and CSRF token.
 * If the user_type is a student, it sends a POST request to store the room ID, while if it's a
 * teacher, it sends a GET request to retrieve the room ID. Once student and teacher have the same room ID,
 * the websocket connection is enstablished with ws/chat/roomId.
 * onmessage: it handles incoming messages and it updates the course name displayed in the chat if the user is a teacher.
 * onclose: it handles the closing of the WebSocket connection.
 * 
 * Reference: https://stackoverflow.com/questions/73354115/how-do-i-add-a-csrf-token-to-a-json-fetch-in-js,
 * https://docs.djangoproject.com/en/4.2/howto/csrf/,
 * https://docs.djangoproject.com/en/5.1/ref/csrf/,
 * https://stackoverflow.com/questions/58155039/django-channelschatsocket-onmessage-or-chatsocket-send-does-not-work
*/

// set courseName as global variable
var courseName;

document.addEventListener("DOMContentLoaded", function () {
  // Get the user type from the page and the CSRF token for secure AJAX requests
  var user_type = document.querySelector('#user-type').value;
  var roomIdElement = document.querySelector('#room-id');
  var roomId = roomIdElement ? roomIdElement.value : '';
  var csrfToken = document.querySelector('#csrf-token').value;

  // If the user is a student and roomId is present, store the roomId on the server
  if (user_type === 'student' && roomId) {
    fetch('/store_info/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ room_id: roomId})
    })
    .then(response => response.json())
    .then(data => {
        // Establish WebSocket connection after storing roomId
        setupWebSocket(roomId); 
    })
    .catch(error => console.error('Error storing room ID:', error));
} 
// If the user is a teacher, retrieve the roomId from the server
else if (user_type === 'teacher') {
    fetch('/get_info/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
      if (data.room_id) {
        var roomId = data.room_id;
        // Establish WebSocket connection after retrieving roomId
        setupWebSocket(roomId); 
    } else {
        console.error('Room ID or Course Name not found for teacher');
    }
    })
    .catch(error => console.error('Error retrieving room ID:', error));
} 
// If the roomId is already set, establish the WebSocket connection directly
else if (roomId) {
    // Establish WebSocket connection if roomId is already set
    setupWebSocket(roomId); 
} else {
    console.error('Room ID is not defined or invalid');
}


  // Function to setup WebSocket connection
  function setupWebSocket(roomId) {
    // Get the course name from the page
    courseName = document.querySelector('#chat-room-name').textContent.trim();

      if (!roomId || roomId === 'undefined') {
          console.error('Cannot establish WebSocket connection, roomId is invalid.');
          return;
      }

      // Connect to the WebSocket server
      const chatSocket = new WebSocket(
          `ws://${window.location.host}/ws/chat/${roomId}/`
      );

      // Handle WebSocket events onmessage
      chatSocket.onmessage = function (e) {
          const data = JSON.parse(e.data);
          const message = data.message;
          const author = data.author;
          const courseNameFromWebSocket = data.course_name;
          
          // Append the received message to the chat log
          if (message) {
              document.querySelector('#chat-log').value += `${author}: ${message}\n`;
          }

          if (user_type === 'teacher') {
              if (courseNameFromWebSocket) {
                // Update course name if received from WebSocket
                document.querySelector('#chat-room-name').textContent = courseNameFromWebSocket.trim();
              }
          }
        };
      
      // Handle WebSocket closure
      chatSocket.onclose = function (e) {
          console.error('Chat socket closed unexpectedly');
      };

      // Submit message on pressing Enter key
      document.querySelector('#chat-message-input').onkeyup = function (e) {
          if (e.keyCode === 13) {  
              document.querySelector('#chat-message-submit').click();
          }
      };

      // Send message when submit button is clicked
      document.querySelector('#chat-message-submit').onclick = function () {
          const messageInputDom = document.querySelector('#chat-message-input');
          const message = messageInputDom.value;
          const author = document.querySelector('#author').value;

          chatSocket.send(JSON.stringify({
              'message': message,
              'author': author,
              'course_name': courseName
          }));
          // Clear message input field
          messageInputDom.value = '';
      };

      // Handle exiting chat and redirect user based on their role
      document.querySelector('#exit-chat-button').onclick = function () {
        chatSocket.send(JSON.stringify({
          'message': `${document.querySelector('#author').value} has left the chat.`,
          'author': 'System',
          'type': 'notification' 
        }));
          chatSocket.close();
          if (user_type === 'student') {
            // Redirect to the course page for students
            window.location.href = `/course/${roomId}/`;  
        } else if (user_type === 'teacher') {
            var teacherPk = document.querySelector('#teacher-pk').value;
            // Redirect to the teacher home page
            window.location.href = `/teacher/${teacherPk}/`;  
        }
      };
  }
});
