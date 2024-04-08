    function addRule() {
        var ruleInput = document.getElementById("ruleInput");
        var ruleValue = ruleInput.value.trim();

        if (ruleValue === "") {
            Swal.fire({
                title: "Rules cannot be empty!",
                icon: "warning"
              });
            return;
        }

        var rulesContainerWrapper = document.getElementById("rulesContainerWrapper");
        rulesContainerWrapper.style.display = "block";

        var rulesContainer = document.getElementById("rulesContainer");
        var ruleElement = document.createElement("div");
        ruleElement.textContent = ruleValue;
        rulesContainer.appendChild(ruleElement);

        ruleInput.value = ""; // Clear input field after adding rule
        updateHiddenRulesInput();
    }

    function updateHiddenRulesInput() {
        var rulesContainer = document.getElementById("rulesContainer");
        var rules = rulesContainer.querySelectorAll("div");
        var hiddenRulesInput = document.getElementById("hiddenRulesInput");
        var rulesText = [];

        rules.forEach(function (rule) {
            rulesText.push(rule.textContent);
        });

        hiddenRulesInput.value = rulesText.join(", ");
    }


    var ruleCounter = 1; // Counter for numbering rules

    function addRule() {
        var ruleInput = document.getElementById("ruleInput");
        var ruleValue = ruleInput.value.trim();

        if (ruleValue === "") {
            Swal.fire({
                title: "Rules cannot be empty!",
                icon: "warning"
              });
            return;
        }

        var rulesContainerWrapper = document.getElementById("rulesContainerWrapper");
        rulesContainerWrapper.style.display = "block";

        var rulesContainer = document.getElementById("rulesContainer");
        var ruleElement = document.createElement("div");
        ruleElement.textContent = ruleCounter + ". " + ruleValue; // Include numbering
        rulesContainer.appendChild(ruleElement);

        ruleInput.value = ""; // Clear input field after adding rule
        updateHiddenRulesInput();

        ruleCounter++; // Increment the rule counter
    }


    function validateForm() {
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        var isChecked = false;
        checkboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                isChecked = true;
            }
        });
        if (!isChecked) {
            Swal.fire({
                title: "Plsease Select at least one amenities!",
                icon: "warning"
              });
            return false; // Prevent form submission
        }
        return true; // Allow form submission
    }


document.getElementById('roomImage').addEventListener('change', function() {
    var files = this.files;
    if (files.length < 3) {
        Swal.fire({
            title: "Please upload at least 3 images.",
            icon: "warning"
            });
        document.getElementById('submitButton').setAttribute('disabled', 'disabled');
    } else {
        document.getElementById('submitButton').removeAttribute('disabled');
    }
});