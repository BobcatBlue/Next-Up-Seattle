"use strict";

const btnOpenSideNav = document.querySelector(".btnOpenNav");
const btnCloseSideNav = document.querySelector(".btnCloseNav");
const sideNav = document.querySelector(".sideNav");

const btnShowMusic = document.querySelector(".show-music");
const btnShowArt = document.querySelector(".show-art");
const btnShowPerformance = document.querySelector(".show-performance");
const btnShowVenues = document.querySelector(".show-venues")

const music_view = document.querySelector(".liveMusic")
const art_view = document.querySelector(".art");
const performance_view = document.querySelector(".performance");
const venue_view = document.querySelector(".venues");

const btnsExpand = document.querySelectorAll(".expander");
const collapsableElements = document.querySelectorAll(".rest_of_events");



btnOpenSideNav.addEventListener("click", function() {
    sideNav.style.width = "250px";
});

btnCloseSideNav.addEventListener("click", function() {
    sideNav.style.width = "0px";
});


for(let i = 0; i < btnsExpand.length; i++) {
    btnsExpand[i].addEventListener("click", function() {
        let btnClicked = btnsExpand[i].classList.contains("clicked");

        console.log(btnsExpand[i].classList);

        if (btnClicked === false) {
            for (let x = 0; x < collapsableElements.length; x++) {
                const currentElement = collapsableElements[x];

                if (currentElement.classList.contains("hidden") === false) {
                    currentElement.classList.add("hidden");


                    let button_class_string = ".";
                    for (let y = 1; y < currentElement.classList.length - 2; y++) {
                        button_class_string = button_class_string + currentElement.classList[y] + ".";
                    }
                    button_class_string = button_class_string + "expander";

                    document.querySelector(button_class_string).classList.remove("clicked");
                    document.querySelector(button_class_string).textContent = "+";
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

            btnsExpand[i].classList.remove("clicked");
            btnsExpand[i].textContent = "+";
            document.querySelector(class_string2).classList.add("hidden");
        }
    })
}


