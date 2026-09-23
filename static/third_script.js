"use strict";

const btnsExpand = document.querySelectorAll(".expander");
const collapsableElements = document.querySelectorAll(".rest_of_events");

console.log(btnsExpand);
console.log(collapsableElements);

for(let i = 0; i < btnsExpand.length; i++) {
    console.log(btnsExpand[i].classList.length);
    console.log("");

    btnsExpand[i].addEventListener("click", function() {
        let btnClicked = btnsExpand[i].classList.contains("clicked");  // boolean value
        console.log(btnClicked);

        console.log(btnsExpand[i].classList);



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