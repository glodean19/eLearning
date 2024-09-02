/**
 * When the message student_removed is received, it retrieves the student and course IDs from the message data. 
 * Either it removes the course and the status update from the student page in the list
 * of enrolled courses and the name of the student from the course_detail page.
 */



document.addEventListener("DOMContentLoaded", function() {
    // Function to get the context from the URL path
    function getContextId() {
        const path = window.location.pathname;
        const courseIdMatch = path.match(/\/course\/(\d+)\//);
        const studentIdMatch = path.match(/\/student\/(\d+)\//);

        // If course ID is found, return context as 'course' or 'student' with its ID
        if (courseIdMatch) {
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

    // Construct the WebSocket URL based on the context (course or student)
    const socketUrl = `ws://${window.location.host}/ws/remove-student/${context.type}/${context.id}/`;
    const removeSocket = new WebSocket(socketUrl);

    removeSocket.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);

            // Check if the message type is 'student_removed'
            if (data.type === 'student_removed') {
                const studentId = data.student_id;
                const courseId = data.course_id;

                // If the context is 'course', remove the student from the enrolled students list
                if (context.type === 'course') {
                    const enrolledStudentsList = document.getElementById('enrolled-students-list');
                    if (enrolledStudentsList) {
                        const studentItem = enrolledStudentsList.querySelector(`[data-student-pk="${studentId}"]`);
                        if (studentItem) {
                            // Remove the student item from the DOM
                            studentItem.remove();
                        }
                    }
                } 
                // If the context is 'student', remove the course from the enrolled courses list
                else if (context.type === 'student') {
                    const enrolledCoursesList = document.querySelector('.list-group');
                    if (enrolledCoursesList) {
                        // Find the course item in the enrolled courses list
                        const courseItem = enrolledCoursesList.querySelector(`[data-course-id="${courseId}"]`);
                        if (courseItem) {
                            courseItem.remove(); // Remove the course item from the DOM
                        }
                    }
                
                    // Remove all status updates associated with this course
                    const statusUpdateItems = document.querySelectorAll(`.list-group-item[data-course-id="${courseId}"]`);
                    statusUpdateItems.forEach(function(statusUpdateItem) {
                        statusUpdateItem.remove(); 
                    });
                }
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    };

});
