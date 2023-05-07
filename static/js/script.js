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

    if (first_name == "" || middle_name == "" || last_name == "" || mail == "" || password == "") {
        fail = "Заполните все поля";
    }

    if (password.length > 30 || password.length < 8) {
        fail = "Пароль должен быть от 8 до 30 символов";
    }

    if (password != password_repeat) {
        fail = "Пароли должны совпадать";
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

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}

function onLoad() {
    document.getElementById("loading").style.display = "none";
}

var prevScrollpos = window.pageYOffset;
window.onscroll = function() {
    var currentScrollPos = window.pageYOffset;
    if (prevScrollpos > currentScrollPos) {
        document.getElementsByClassName("header")[0].style.top = "0";
    } else {
        document.getElementsByClassName("header")[0].style.top = "-70px";
    }
    prevScrollpos = currentScrollPos;
}

document.getElementById("edit-button").onclick = function() {
    location.href = "/edit_profile";
}