

function getUsers() {
    return requestAPI('/users', 'GET')
}

function createUser() {
    //TODO
    //users/create-account
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
            $("#login-error").text('Your username is wrong!')
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