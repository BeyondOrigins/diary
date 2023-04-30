function onAuth(form) {
    login = form.login.value;
    password = form.password.value;

    var fail = "";

    if (login == "" || password == "") {
        fail = "Заполните все поля";
    }

    if (fail == "") {
        return true;
    }

    else {
        document.getElementById("error").innerHTML = fail;
        return false;
    }
}

function toRegistrationPage() {
    location.href = "/register";
}