// JavaScript to close the messages after 3 seconds (3000 milliseconds)
setTimeout(function() {
var toastElement = document.getElementById('toast-success');
if (toastElement) {
    toastElement.style.display = 'none';
}
}, 3000);

// View entered password //
function togglePasswordVisibility(inputId) {
    var passwordInput = document.getElementById(inputId);
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Get the user type field and document image field
    const userTypeField = document.getElementById("registrationType");
    const documentImageField = document.getElementById("documentImageField");
    const documentImageInput = document.getElementById("id_document_image");

    // Add an event listener to the user type field
    if (userTypeField) {
        userTypeField.addEventListener("change", toggleDocumentImageVisibility);
    }

    function toggleDocumentImageVisibility() {
        console.log('hi')
        // Check the value of the user type field
        const userType = userTypeField.value;

        // Toggle visibility of the document image field based on the user type
        if (userType === "owner") {
            documentImageField.style.display = "block";
            documentImageInput.required = true;
        } else {
            documentImageField.style.display = "none";
            documentImageInput.required = false;
        }
    }
});
