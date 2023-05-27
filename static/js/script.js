function checkPassword() {
    var password = document.getElementsByName("password")[0].value;
    var password_repeat = document.getElementsByName("password_repeat")[0].value;
    var el = document.getElementsByName("password_repeat")[0];
    if (password_repeat != password) {
        el.style = "background-color: rgba(247, 85, 85, 0.205)";
    }
    if (password_repeat == "") {
        el.style = "background-color: var(--form-color)";
    }
    if (password_repeat == password && password != "") {
        el.style = "background-color: rgba(90, 247, 85, 0.205)";
    }
}

function onAuth(form) {
    var mail = form.login.value;
    var password = form.password.value;

    var fail = "";

    if (mail == "" || password == "") {
        fail = "Заполните все поля";
    }

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}

function onRegistration(form) {
    var first_name = form.first_name.value;
    var middle_name = form.middle_name.value;
    var last_name = form.last_name.value;
    var mail = form.mail.value;
    var password = form.password.value;
    var password_repeat = form.password_repeat.value;

    var fail = "";

    if (password.length > 30 || password.length < 8) {
        fail = "Пароль должен быть от 8 до 30 символов";
    }

    if (password != password_repeat) {
        fail = "Пароли должны совпадать";
    }

    if (first_name == "" || middle_name == "" || last_name == "" || mail == "" || password == "") {
        fail = "Заполните все поля";
    }

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}

function onProfileChange(form) {
    var first_name = form.first_name.value;
    var middle_name = form.middle_name.value;
    var last_name = form.last_name.value;
    var mail = form.mail.value;

    var fail = "";

    if (first_name == "" || middle_name == "" || last_name == "" || mail == "") {
        fail = "Все поля должны быть полными";
    }

    if (first_name.length >= 40 || middle_name.length >= 40 || last_name.length >= 40) {
        fail = "Имя, Фамилия или Отчество слишком длинные";
    }

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}

function onLoad() {
    document.getElementById("loading").style.display = "none";
}

// убирать заголовок при промотке вниз
var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
    var currentScrollPos = window.pageYOffset;
    if (prevScrollpos > currentScrollPos) {
        document.getElementsByClassName("header")[0].style.top = "0";
        document.getElementsByClassName("theme-switch-container")[0].style.top = "100px";
        document.getElementsByClassName("scheme-select-container")[0].style.top = "135px";
    } else {
        document.getElementsByClassName("header")[0].style.top = "-70px";
        document.getElementsByClassName("theme-switch-container")[0].style.top = "10px";
        document.getElementsByClassName("scheme-select-container")[0].style.top = "45px";
    }
    prevScrollpos = currentScrollPos;
}

try {
    document.getElementById("edit-button").onclick = function() {
        location.href = "/edit_profile";
    }
}
catch { }

// определить тему
function detectScheme() {
    document.documentElement.setAttribute("data-theme", localStorage.getItem("theme") || "light");
    document.documentElement.setAttribute("color-scheme", localStorage.getItem("scheme") || "purple");
}

detectScheme();
const themeSwitch = document.querySelector('#theme-switch');

if (document.documentElement.getAttribute("data-theme") == "dark"){
    themeSwitch.checked = true;
}

// установить тему
function switchTheme(e) {
    if (e.target.checked) {
        localStorage.setItem('theme', 'dark');
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
        document.documentElement.setAttribute('data-theme', 'light');
    }
}

themeSwitch.addEventListener("change", switchTheme, false);

// выезжание окна выбора тем
var showSchemeSettings = false;
const settingsSign = document.querySelector("#color-scheme-setting");
settingsSign.addEventListener("click", function(e) {
    if (!showSchemeSettings) {
        document.querySelector(".scheme-select").style.right = "10px";
        document.querySelector(".scheme-select-container").style.right = "240px";
        document.querySelector("#color-scheme-setting").style = "transform: rotateZ(-360deg);";
        showSchemeSettings = true;
    }
    else {
        document.querySelector(".scheme-select").style.right = "-240px";
        document.querySelector(".scheme-select-container").style.right = "10px";
        document.querySelector("#color-scheme-setting").style = "transform: rotateZ(0deg);";
        showSchemeSettings = false;
    }
}, false);

// сменить цветовую схему
function switchScheme(e) {
    let scheme_color = e.target.getAttribute("data-color");
    localStorage.setItem("scheme", scheme_color);
    document.documentElement.setAttribute('color-scheme', scheme_color);
    document.querySelector(".scheme-color-selected").classList.toggle("scheme-color");
    e.target.classList.toggle("scheme-color-selected");
}

var color_buttons = Array.from(document.getElementsByClassName("scheme-color"))
.concat(Array.from(document.getElementsByClassName("scheme-color-selected")));

// назначить диспетчер событий для всех элементов с классом scheme-color или scheme-color-selected
color_buttons.forEach(function(element) {
    element.addEventListener("click", switchScheme, false);
});
