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