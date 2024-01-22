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
