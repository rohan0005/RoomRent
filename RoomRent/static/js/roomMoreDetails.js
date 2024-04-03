// Get the checkbox element
var checkbox = document.getElementById("checked-checkbox");

// Get the container of fine fields
var fineFields = document.getElementById("fine-fields");

// Get the input fields
var fineAmountInput = document.getElementById("fine-amount");
var fineReasonInput = document.getElementById("fine-reason");

checkbox.addEventListener("change", function() {
    // Check if the checkbox is checked
    if (this.checked) {
        // Show the fine fields container
        fineFields.style.display = "block";

        fineAmountInput.setAttribute("required", "");
        fineReasonInput.setAttribute("required", "");
    } else {
        fineFields.style.display = "none";
        fineAmountInput.removeAttribute("required");
        fineReasonInput.removeAttribute("required");
    }
});
