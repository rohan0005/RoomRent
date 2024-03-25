  
  var calculateBtns = document.querySelectorAll(".calculateBtn");
  calculateBtns.forEach(function(btn) {
      btn.addEventListener("click", function() {
        var previousUnit = parseInt(
            document.getElementById("previousUnit").value
          );
          console.log(previousUnit);
    
          var currentUnit = parseInt(document.getElementById("currentUnit").value);
          var electricityRate = parseInt(
            document.getElementById("electricityRate").value
          );
          var rentAmount = parseInt(document.getElementById("rentAmount").value);
          var waterRent = parseInt(document.getElementById("waterRent").value);
          var trashRent = parseInt(document.getElementById("trashRent").value);
    
          if (!isNaN(currentUnit)) {
            var newUnit = currentUnit - previousUnit;
    
            var electricityAmount = newUnit * electricityRate;
            var totalAmount =
              electricityAmount + rentAmount + waterRent + trashRent;
    
            document.getElementById("electricityAmount").textContent =
              "Rs. " + electricityAmount;
            document.getElementById("totalAmount").textContent =
              "Rs. " + totalAmount;
    
            document.getElementById("totalAmount-hidden").value = totalAmount;
            document.getElementById("electricityUnit-hidden").value = newUnit;
            document.getElementById("electricityAmount-hidden").value =
              electricityAmount;
    
            document.getElementById("electricityUnit").textContent =
              newUnit + " Unit";
            document.getElementById("previousUnit-hidden").value = previousUnit;
            document.getElementById("currentUnit-hidden").value = currentUnit;
    
            // Show the result div
            document.getElementById("calculationResult").classList.remove("hidden");
    
            document.getElementById("electricityDetails").classList.add("hidden");
          } else {
            alert("Please enter a valid current unit.");
          }
      });
  });
  