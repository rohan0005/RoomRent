var calculateBtns = document.querySelectorAll(".calculateBtn");

function calculate(id) {
  var previousUnit = parseInt(document.getElementById(`previousUnit-${id}`).value);
  var currentUnit = parseInt(document.getElementById(`currentUnit-${id}`).value);
  var electricityRate = parseInt(
    document.getElementById(`electricityRate-${id}`).value
  );
  var rentAmount = parseInt(document.getElementById(`rentAmount-${id}`).value);
  var waterRent = parseInt(document.getElementById(`waterRent-${id}`).value);
  var trashRent = parseInt(document.getElementById(`trashRent-${id}`).value);

  if (currentUnit && previousUnit) {
    var newUnit = currentUnit - previousUnit;

    var electricityAmount = newUnit * electricityRate;
    var totalAmount = electricityAmount + rentAmount + waterRent + trashRent;

    document.getElementById(`electricityAmount-${id}`).textContent =
      "Rs. " + electricityAmount;
    document.getElementById(`totalAmount-${id}`).textContent = "Rs. " + totalAmount;

    document.getElementById(`totalAmount-hidden-${id}`).value = totalAmount;
    document.getElementById(`electricityUnit-hidden-${id}`).value = newUnit;
    document.getElementById(`electricityAmount-hidden-${id}`).value =
      electricityAmount;

    document.getElementById(`electricityUnit-${id}`).textContent = newUnit + " Unit";
    document.getElementById(`previousUnit-hidden-${id}`).value = previousUnit;
    document.getElementById(`currentUnit-hidden-${id}`).value = currentUnit;

    // Show the result div
    document.getElementById(`calculationResult-${id}`).classList.remove("hidden");

    document.getElementById(`electricityDetails-${id}`).classList.add("hidden");
  } else {

    Swal.fire({
      title: "Please enter a valid unit !!",
      icon: "error"
    });

  }
}
