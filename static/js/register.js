function checkPassword() {
    var password = document.getElementsByName("pswrd")[0].value;
    var password_repeat = document.getElementsByName("pswrd_repeat")[0].value;
    var el = document.getElementsByName("pswrd_repeat")[0];
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