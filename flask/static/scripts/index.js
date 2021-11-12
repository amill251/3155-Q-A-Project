

function getUsers() {
    return requestAPI('/users', 'GET')
}

function signup() {
    let nameArr = $('#form3Example1c').val().split(' ');

    let firstName = nameArr[0];
    let lastName = nameArr[1];
    let username = $('#form3Example2c').val();
    let password = $('#form3Example3c').val();

    if ($('#form3Example3c').val() !== $('#form3Example3cd').val()) {
        $('#auth-err').text('Please match your passowrd!');
        return;
    }

    $('#auth-err').text('');

    let requestBody = {
        "first_name": firstName,
        "last_name": lastName,
        "_username": username,
        "_password": password
    }

    callback = function (data) {
        //TODO
        if (data.succeed) {
            window.location.replace("feed");
        }
        //if success = false, let user know the error (either password or user invalid)
    }

    return requestAPI('/users/create-account', 'POST', requestBody, callback);
}

function login() {
    let username = $('#usernameInput').val();
    let password = $('#passwordInput').val();

    let requestBody = {
        "_username": username,
        "_password": password
    }

    callback = function (data) {
        //TODO
        console.log(data)
        if (data.succeed) {
            window.location.replace("feed");
        } else {
            $("#login-error").text(data.message)
        }
        //if success = false, let user know the error (either password or user invalid)
    }

    return requestAPI('/users/login', 'POST', requestBody, callback)
}

function getQuestions(callback) {
    return requestAPI('/questions', 'GET', null, callback)
}

function route(route) {
    window.location.replace(route);
}

function requestAPI(endpoint, method, body, callback) {
    let settings = {
        "url": "http://localhost:5000/api" + endpoint,
        "method": method,
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": JSON.stringify(body),
        "success": callback
    };

    console.log(settings);

    return $.ajax(settings).done();
}