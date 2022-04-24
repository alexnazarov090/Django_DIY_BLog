// SideBar
const body = document.body;
const sideBar = document.querySelector(".sidebar");
const hamburgerMenuBtn = document.querySelector(".hamburger-menu-btn");
const navLinks = document.querySelectorAll(".nav__link");


hamburgerMenuBtn.addEventListener('click', sideBarToggle);
navLinks.forEach((link) => {
    link.addEventListener('click', removeSideBar);
});

function sideBarToggle() {
    if (!sideBar.classList.contains("sidebar-visible")) {
        sideBar.classList.add("sidebar-visible");
        this.classList.add("sidebar-visible");
        body.classList.add("noscroll");

    } else {
        sideBar.classList.remove("sidebar-visible");
        this.classList.remove("sidebar-visible");
        body.classList.remove("noscroll");
    }
}

function removeSideBar() {
    if (sideBar.classList.contains("sidebar-visible")) {
        
        sideBar.classList.remove("sidebar-visible");
        hamburgerMenuBtn.classList.remove("sidebar-visible");
        body.classList.remove("noscroll");
    } 
}

window.addEventListener('load', resizeMostFreqWords);

function resizeMostFreqWords() {
    const mostFreqWords = document.querySelectorAll(".most_freq_words__list-item a");

    mostFreqWords.forEach((word, index) => {
        if (index <= 10) {
            word.style.fontSize = "4rem";
            word.style.fontWeight = "600";
        } else if (index > 10 && index <= 20) {
            word.style.fontSize = "3rem";
            word.style.fontWeight = "400";
        } else if (index > 20) {
            word.style.fontSize = "2rem";
            word.style.fontWeight = "200";
        }
    });
}
