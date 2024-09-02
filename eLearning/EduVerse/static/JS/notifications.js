/**
 * Only the relevant student and teacher pages will display the notifications.
 * When a message is received through the WebSocket, it is parsed as JSON. 
 * Depending on the message type (student_enrolled or update_material), 
 * the script updates the notification messages and the displayed student count, 
 * or it shows notifications about new course materials.
 * updateNotificationMessage: it updates the notification for a new student enrollment; 
 * updateStudentCount: it adjusts the student count for a specific course; 
 * updateMaterialsNotification: it notifies the user about new materials uploaded for a course.
 * 
 * Reference: https://medium.com/geekculture/designing-a-websocket-client-with-notifications-in-reactjs-reformers-reactjs-implementation-c669daf27d46,
 * https://dev.to/novu/building-a-chat-browser-notifications-with-react-websockets-and-web-push-1h1j
 */


document.addEventListener("DOMContentLoaded", function() {
    const path = window.location.pathname;

    // Determine if the current page is relevant for notifications (either a teacher or student page)
    const isRelevantPage = path.includes('/teacher/') || path.includes('/student/');
    
    // Get notification elements from the DOM
    const notificationContainer = document.getElementById('notification-container');
    const notificationMessage = document.getElementById('notification-message');
    const studentNotificationMessage = document.getElementById('student-notification-message');

    // Check if the page is relevant and if notification elements exist in the DOM
    if (isRelevantPage && (!notificationContainer || (!notificationMessage && !studentNotificationMessage))) {
        console.error('Notification elements not found in the DOM.');
        return;
    }

    // Function to extract context (teacher, student, or course) and ID from the URL
    function getContextId() {
        const teacherIdMatch = path.match(/\/teacher\/(\d+)\//);
        const courseIdMatch = path.match(/\/course\/(\d+)\//);
        const studentIdMatch = path.match(/\/student\/(\d+)\//);

        if (teacherIdMatch) {
            return { type: 'teacher', id: teacherIdMatch[1] };
        } else if (courseIdMatch) {
            return { type: 'course', id: courseIdMatch[1] };
        } else if (studentIdMatch) {
            return { type: 'student', id: studentIdMatch[1] };
        } else {
            console.error('Context ID not found in URL');
            return null;
        }
    }

    const context = getContextId();

    if (!context) {
        return;
    }

        // Initialize WebSocket connection only if the page is relevant for notifications
        const socketUrl = `ws://${window.location.host}/ws/notifications-change/${context.type}/${context.id}/`;
        const notificationSocket = new WebSocket(socketUrl);

        // Handle incoming WebSocket messages
        notificationSocket.onmessage = function(event) {
            console.log('Raw WebSocket message:', event.data)
            try {
                const data = JSON.parse(event.data);
                // if message is student_enrolled
                if (data.type === 'student_enrolled') {
                    // Update notification for a new student enrollment
                    updateNotificationMessage(data.student_name, data.course_name);
                    // Update the student count in the course
                    updateStudentCount(data.enrolled_student_count, data.course_id);
                    // if message is update_material
                } else if (data.type === 'update_material') {
                    //Update notification for new course materials
                    updateMaterialsNotification(data.course_name);
                } else {
                    console.error('Unsupported message type:', data.type);  
                }
            } catch (error) {
                console.error('Error handling WebSocket message:', error);
            }
        };

    // Function to update the notification message for a new student enrollment
    function updateNotificationMessage(studentName, courseName) {
        if (notificationContainer && notificationMessage) {
            const message = `${studentName} has enrolled in the course ${courseName}.`;
            notificationMessage.textContent = message;
            // Show the notification container
            notificationContainer.style.display = 'block'; 
        }
    }

    function updateStudentCount(courseId) {
        // Select the course element by the data attribute
        const courseElement = document.querySelector(`#course-${courseId} .enrolled-student-count`);
    
        if (courseElement) {
            // Parse the current count as an integer and update it
            var currentCount = parseInt(courseElement.textContent, 10);
            currentCount += 1; 
            courseElement.textContent = currentCount;
        } else {
            console.error(`Course element with ID ${courseId} not found.`);
        }
    }

    // Function to update the notification message for new course materials
    function updateMaterialsNotification(courseName) {
        if (notificationContainer && studentNotificationMessage) {
            const message = `New material has been uploaded on ${courseName}.`;
            // Set the text content of the notification message element
            studentNotificationMessage.textContent = message;
            notificationContainer.style.display = 'block';
        }
    }

    // Hide the notification container when it is clicked
    if (notificationContainer) {
        notificationContainer.addEventListener('click', function() {
            notificationContainer.style.display = 'none';
        });
    }
});
