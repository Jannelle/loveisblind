// ================ Messages ================ //
// Function to show an error message
function showErrorMessage(message) {
    // Display the error message (you can customize this part)
    var errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';

    // Hide the message after a few seconds (you can adjust the timeout)
    setTimeout(function () {
        errorDiv.style.display = 'none';
    }, 8000); // Hide after 3 seconds
}

function showConfirmationMessage(message) {
    // Display the confirmation message (you can customize this part)
    var confirmationDiv = document.getElementById('confirmationMessage');
    confirmationDiv.textContent = message;
    confirmationDiv.style.display = 'block';

    // Hide the message after a few seconds (you can adjust the timeout)
    setTimeout(function () {
        confirmationDiv.style.display = 'none';
    }, 3000); // Hide after 3 seconds
};
