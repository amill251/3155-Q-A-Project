function getUsers() {
    return requestAPI('/users', 'GET');
}

function getQuestions(callback) {
    return requestAPI('/questions', 'GET', null, callback);
}

function createQuestion(questionBody, callback) {
    return requestAPI('/questions', 'POST', questionBody, callback);
}

function postLogin(loginBody, callback) {
    return requestAPI('/users/login', 'POST', loginBody, callback);
}

function postSignup(signupBody, callback) {
    return requestAPI('/users/create-account', 'POST', signupBody, callback);
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