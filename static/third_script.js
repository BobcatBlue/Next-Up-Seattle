"use strict";

const btnsExpand = document.querySelectorAll(".expander");
const collapsableElements = document.querySelectorAll(".rest_of_events");

const hamburger = document.getElementById("hamburger");
const sideMenu = document.getElementById("sideMenu");


hamburger.addEventListener("click", function () {
    sideMenu.classList.toggle("open");
});


document.addEventListener("click", function (event) {
    if (
        sideMenu.classList.contains("open") &&
        !sideMenu.contains(event.target) &&
        !hamburger.contains(event.target)
    ) {
        sideMenu.classList.remove("open");
    }
});

// define constant for neighborhood selector
const music_neighborhood = document.getElementById("neighborhoods");
const cal_cards = document.querySelectorAll(".cal_card")


// If the neighborhood selector is changed, change which cal cards are displayed
music_neighborhood.addEventListener("change", function() {
    const selected_neighborhood = music_neighborhood.options[music_neighborhood.selectedIndex].text;
    // console.log(selected_neighborhood);

    for(let i = 0; i < cal_cards.length; i++){

        // If "All" has been selected, do nothing
        if (selected_neighborhood == "All") {
            cal_cards[i].classList.remove("removed");
        }

        // If "Downtown & SODO" is selected
        else if (selected_neighborhood == "Downtown & SODO") {
            if (cal_cards[i].id == "Downtown" || cal_cards[i].id == "SODO") {
                cal_cards[i].classList.remove("removed");
            } else {
                cal_cards[i].classList.add("removed");
            }
        }

        // If any selection besides "All" or "Downtown & SODO" is selected, behave nominally
        else {
            if (cal_cards[i].id == selected_neighborhood) {
            cal_cards[i].classList.remove("removed");
            }

            else if (cal_cards[i].id != selected_neighborhood) {
            cal_cards[i].classList.add("removed");
            }
        }

    }
})



//console.log(btnsExpand);
//console.log(collapsableElements);


for(let i = 0; i < btnsExpand.length; i++) {
    //console.log(btnsExpand[i].classList.length);
    //console.log("");

    btnsExpand[i].addEventListener("click", function() {
        let btnClicked = btnsExpand[i].classList.contains("clicked");  // boolean value
        //console.log(btnClicked);
        //console.log(btnsExpand[i].classList);
        if (btnClicked === false) {

            console.log(collapsableElements);
            for (let x = 0; x < collapsableElements.length; x++) {
                const currentElement = collapsableElements[x];
                console.log("CLASS LIST " + x);
                console.log(currentElement.classList);

                if (currentElement.classList.contains("hidden") === false) {
                    //console.log("This list does not contain Hidden:");
                    console.log(currentElement.classList);
                    currentElement.classList.add("hidden");
                    //console.log("There I fixed it");
                    console.log(currentElement.classList);

                    let button_class_string = ".";
                    for (let y = 1; y < currentElement.classList.length - 2; y++) {
                        button_class_string = button_class_string + currentElement.classList[y] + ".";
                    }
                    button_class_string = button_class_string + "expander";

                    document.querySelector(button_class_string).classList.remove("clicked");
                    document.querySelector(button_class_string).textContent = "+";

                    console.log(button_class_string);
                }

            }


            let class_string = ".";
            for(let x = 0; x < btnsExpand[i].classList.length; x++) {
                if(x < btnsExpand[i].classList.length - 1) {
                    class_string = class_string + btnsExpand[i].classList[x] + ".";
                } else {
                    class_string = class_string + "expandable";
                }
            }

            console.log(class_string);

            document.querySelector(class_string).classList.remove("hidden");
            btnsExpand[i].classList.add("clicked");
            btnsExpand[i].textContent = "-";
        }
        else if (btnClicked === true) {
            let class_string2 = ".";
            for(let x = 0; x < btnsExpand[i].classList.length - 1; x++) {
                if(x < btnsExpand[i].classList.length - 2) {
                    class_string2 = class_string2 + btnsExpand[i].classList[x] + ".";
                } else {
                    class_string2 = class_string2 + "expandable";
                }
            }

            console.log(btnClicked);
            btnsExpand[i].classList.remove("clicked");
            btnsExpand[i].textContent = "+";
            document.querySelector(class_string2).classList.add("hidden");
        }
    })
}