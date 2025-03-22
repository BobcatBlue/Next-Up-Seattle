function myFunction() {
  x.classList.toggle("change");
}

function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

function toggleView(view) {
    const mapButton = document.getElementById('mapButton');
    const listButton = document.getElementById('listButton');
    const mapView = document.getElementById('mapView');
    const listView = document.getElementById('listView');

    if (view == "map") {
        mapButton.classList.add('active');
        listButton.classList.remove('active');
        mapView.style.display = 'block';
        listView.style.display = 'none';
    }
    else {
        listButton.classList.add('active');
        mapButton.classList.remove('active');
        listView.style.display = 'block';
        mapView.style.display = 'none';
    }
}

function mapPopUp(ven) {
    console.log("Clicked:", ven); // Debugging message
    var popup = document.getElementById("popup")
    var content = document.getElementById("popup-content")

    if(!dictionary[ven]) {
        console.warn("No data found for", ven);
        return;
    }

    content.innerHTML = `
        <div style="padding: 10px; padding-top: 40px; padding-right: 25px;">
            <strong>${ven}</strong><br>
            ${dictionary[ven][2]}<br>
            ${dictionary[ven][3]}<br>
        </div>`

    // Find the clicked circle
    var circle = document.querySelector(`circle[onclick*="${ven}"]`);
    if (!circle) {
        console.error("Circle not found:", ven);
        return;
    }

    var rect = circle.getBoundingClientRect();

    popup.style.left = `${rect.left + window.scrollX + 10}px`;
    popup.style.top = `${rect.top + window.scrollY - 40}px`;
    popup.style.display = "block";
}

// Close popup when clicking outside
document.addEventListener("click", function(event) {
    if (!event.target.closest("circle") && event.target.id !== "popup") {
        document.getElementById("popup").style.display = "none";
    }
}, true);

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}