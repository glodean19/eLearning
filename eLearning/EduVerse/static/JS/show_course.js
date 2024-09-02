/** The showCourseDetails function shows the details of the course when clicking on it in the teacher home page.
 *  The clearQueryParameters removes any query parameters from the current URL without reloading the page. 
 * It uses the replaceState method from the browser's history API, which updates the URL displayed in the browser's address bar.
 * This function is called automatically when the page has finished loading.
 * 
 * Reference: https://developer.mozilla.org/en-US/docs/Web/API/History_API/Working_with_the_History_API
 */

function showCourseDetails(courseId) {
    // Hide all elements with the class 'course-details'
    document.querySelectorAll('.course-details').forEach(function(element) {
        element.style.display = 'none';
    });
    // Get the specific course detail element by constructing its ID
    var courseDetailElement = document.getElementById('course-' + courseId);
    // If the course detail element exists
    if (courseDetailElement) {
        // Display the course details for the selected course
        courseDetailElement.style.display = 'block';
        // Remove any existing 'Edit' buttons
        var existingEditButtons = courseDetailElement.querySelectorAll('a.btn.btn-secondary');
        existingEditButtons.forEach(function(button) {
            button.remove();
        });
        // Create the 'Edit' button as a new anchor element
        var editButton = document.createElement('a');
        // Set the href attribute to link to the course detail edit page
        editButton.href = "/course/" + courseId + "/detail/"; 
        // Set the text content of the anchor element to 'Edit'
        editButton.textContent = 'Edit';
        editButton.className = 'btn btn-secondary';
        // Append the 'Edit' button to the course detail element
        courseDetailElement.appendChild(editButton);
    }
}
// Function to clear query parameters from the URL
function clearQueryParameters() {
    // Check if the browser supports the history API's replaceState method
    if (window.history.replaceState) {
        // Construct a new URL only with the protocol, host, and path
        var newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
        // Replace the current URL in the browser's history with the new URL (without refreshing the page)
        window.history.replaceState({}, document.title, newUrl);
    }
}
// Call the clearQueryParameters function when the window has fully loaded
window.onload = clearQueryParameters;