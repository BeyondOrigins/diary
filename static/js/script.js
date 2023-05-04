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

function onProfileChanage(form) {
    var first_name = form.first_name.value();
    var middle_name = form.middle_name.value();
    var last_name = form.last_name.value();
    var mail = form.mail.value();

    var fail = "";

    if (first_name == "" || middle_name == "" || last_name == "" || mail == "") {
        fail = "Заполните все поля";
    }

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}

function onAuth(form) {
    var password = form.password.value();
    var mail = form.mail.value();
    
    var fail = "";
    
    if (password == "" || mail == "") {
        fail = "Заполните все поля";
    }
    
    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }
    
    return true;
}

function onRegistration(form) {
    var first_name = form.first_name.value();
    var middle_name = form.middle_name.value();
    var last_name = form.last_name.value();
    var mail = form.mail.value();
    var password = form.password.value();

    var fail = "";

    if (first_name == "" || middle_name == "" || last_name == "" || mail == "" || password == "") {
        fail = "Заполните все поля";
    }

    if (fail != "") {
        document.getElementById("error").innerHTML = fail;
        return false;
    }

    return true;
}