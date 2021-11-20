function login() {
    console.log('Calling login function');
    let formFalse = false;

    $('input', '#login-form').toArray().forEach((x) => {
        if(!x.checkValidity()) {
            formFalse = true;
            return;
        }
    });

    if(formFalse) {
        return;
    }
    console.log('Calling login function 2');

    let username = $('#usernameInput').val();
    let password = $('#passwordInput').val();

    let requestBody = {
        "_username": username,
        "_password": password
    }

    console.log('Calling login function 3');
    callback = function (data) {
        //TODO
        console.log(data)
        if (data.succeed) {
            console.log('Calling login function 4');
            route("feed");
        } else {
            console.log('Calling login function 5');
            $("#login-error").text(data.message);
        }
        //if success = false, let user know the error (either password or user invalid)
    }

    return postLogin(requestBody, callback);
}

$(document).ready(function() {
    $(document).on('submit', '#login-form', function() {
      return false;
     });
});