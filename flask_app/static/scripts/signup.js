function signup() {

    let formFalse = false;

    $('input', '#signup-form').toArray().forEach((x, i) => {
        if(!x.checkValidity()) {
            formFalse = true;
            return;
        }
    });

    if(formFalse) {
        return;
    }

    let firstName =  $('#first_name').val();
    let lastName =  $('#last_name').val();
    let username = $('#username').val();
    let password = $('#password').val();

    let requestBody = {
        "first_name": firstName,
        "last_name": lastName,
        "_username": username,
        "_password": password
    }

    callback = function (data) {

        if (data.succeed) {
            route("feed");
        } else if (!data.succeed) {
            $('#create-acc-error').text(data.message)
        }

    }

    return postSignup(requestBody, callback);
}

$(document).ready(function() {
    $(document).on('submit', '#signup-form', function() {
      return false;
     });
});