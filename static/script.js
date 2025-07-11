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
console.log(btnsExpand);



btnOpenSideNav.addEventListener("click", function() {
    sideNav.style.width = "250px";
});

btnCloseSideNav.addEventListener("click", function() {
    sideNav.style.width = "0px";
});

btnShowMusic.addEventListener("click", function() {
    console.log("Music button clicked");
    music_view.classList.remove("hidden");
    art_view.classList.add("hidden");
    performance_view.classList.add("hidden");
    venue_view.classList.add("hidden");

});

btnShowArt.addEventListener("click", function() {
    console.log("Art button clicked");
    art_view.classList.remove("hidden");
    performance_view.classList.add("hidden");
    music_view.classList.add("hidden");
    venue_view.classList.add("hidden");

});

btnShowPerformance.addEventListener("click", function() {
    console.log("Performance button clicked");
    performance_view.classList.remove("hidden");
    art_view.classList.add("hidden");
    music_view.classList.add("hidden");
    venue_view.classList.add("hidden");
});

btnShowVenues.addEventListener("click", function() {
    console.log("Performance button clicked");
    performance_view.classList.add("hidden");
    art_view.classList.add("hidden");
    music_view.classList.add("hidden");
    venue_view.classList.remove("hidden");
});


for(let i = 0; i < btnsExpand.length; i++) {
    console.log(btnsExpand[i].classList.length);
    console.log("");

    btnsExpand[i].addEventListener("click", function() {
        let btnClicked = btnsExpand[i].classList.contains("clicked");  // boolean value
        console.log(btnClicked);

        console.log(btnsExpand[i].classList);



        if (btnClicked === false) {
            let class_string = ".";

            for(let x = 0; x < btnsExpand[i].classList.length; x++) {
                if(x < btnsExpand[i].classList.length - 1) {
                    class_string = class_string + btnsExpand[i].classList[x] + ".";
                } else {
                    class_string = class_string + "expandable";
                }
                console.log(class_string);
            }

            console.log(class_string);
            document.querySelector(class_string).classList.remove("hidden");
            btnsExpand[i].classList.add("clicked");
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
            document.querySelector(class_string2).classList.add("hidden");
        }
    })
}