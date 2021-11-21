let jwtToken;

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

function refreshAuth(callback) {
    return requestAPI('/refresh-token', 'GET', null, callback);
}

function route(route) {
    window.location.replace(route)
}

function requestAPI(endpoint, method, body, callback) {
    let settings = {
        "url": "http://localhost:5000/api" + endpoint,
        "method": method,
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": jwtToken
        },
        "data": JSON.stringify(body),
        "success": callback
    };

    return $.ajax(settings).done();
}

function tokenExpired() {
    if(!jwtToken) {
        return true;
    }

    let exp = JSON.parse(atob(jwtToken.replace('Bearer ', '').split('.')[1])).exp - Math.ceil(((new Date().getTime())/1000))
    if(exp > 0) {
        return false;
    } else {
        return true;
    }
}