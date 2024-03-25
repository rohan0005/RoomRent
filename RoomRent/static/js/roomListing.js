    function addRule() {
        var ruleInput = document.getElementById("ruleInput");
        var ruleValue = ruleInput.value.trim();

        if (ruleValue === "") {
            alert("Rule cannot be empty");
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
            alert("Rule cannot be empty");
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

    // Remaining code remains the same


