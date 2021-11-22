

$(document).ready(() => {
    if(cookiesExpired()) {
        $('#login-page').show()
    } else {
        route('feed')
    }
});

function login() {

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


    let username = $('#usernameInput').val();
    let password = $('#passwordInput').val();

    let requestBody = {
        "_username": username,
        "_password": password
    }

    callback = function (data) {
        if (data.succeed) {
            route("feed");
        } else {
            $("#login-error").text(data.message);
        }
    }

    return postLogin(requestBody, callback);
}

$(document).ready(function() {
    $(document).on('submit', '#login-form', function() {
      return false;
     });
});