// DOM content load
document.addEventListener("DOMContentLoaded", function() {
    // Get all modal toggle 
    var modalToggleButtons = document.querySelectorAll("[data-modal-toggle]");

    // Add click event listener to each modal toggle button
    modalToggleButtons.forEach(function(button) {
        button.addEventListener("click", function() {
            // Get the payment ID from the button data-modal-toggle attribute
            var paymentId = this.dataset.modalToggle.split("-")[2];

            // Set the payment ID value in the hidden input field
            document.getElementById("paymentHistoryID").value = paymentId;
        });
    });
});