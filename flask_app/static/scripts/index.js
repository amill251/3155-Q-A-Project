let jwtToken;

function getUsers() {
    return requestAPI('/users', 'GET');
}

function getQuestions(callback, queryBody) {
    return requestAPI('/questions' + queryBody, 'GET', null, callback);
}

function getQuestion(callback, questionBody) {
    return requestAPI('/questions' + questionBody, 'GET', null, callback);
}

function postQuestionDelete(callback, questionBody) {
    return requestAPI('/questions/delete', 'POST', JSON.stringify(questionBody), callback);
}

function postQuestionReport(callback, questionBody) {
    return requestAPI('/report', 'POST', JSON.stringify(questionBody), callback);
}

function postQuestionEdit(callback, questionBody) {
    return requestAPI('/questions/edit', 'POST', JSON.stringify(questionBody), callback);
}


function createQuestion(questionBody, callback) {
    return requestAPI('/questions', 'POST', JSON.stringify(questionBody), callback);
}

function getAnswers(callback, questionBody) {
    return requestAPI('/answers' + questionBody, 'GET', null, callback);
}

function createAnswer(answerBody, callback) {
    return requestAPI('/answers', 'POST', JSON.stringify(answerBody), callback);
}

function postLogin(loginBody, callback) {
    return requestAPI('/users/login', 'POST', JSON.stringify(loginBody), callback);
}

function postSignup(signupBody, callback) {
    return requestAPI('/users/create-account', 'POST', JSON.stringify(signupBody), callback);
}

function refreshAuth(callback) {
    return requestAPI('/refresh-token', 'GET', null, callback);
}

function serverLogout(callback) {
    return requestAPI('/users/logout', 'POST', null, callback);
}

function postVote(callback, voteBody) {
    return requestAPI('/votes', 'POST', JSON.stringify(voteBody), callback);
}

function postReaction(callback, reactBody) {
    return requestAPI('/reaction', 'POST', JSON.stringify(reactBody), callback);
}

function route(route) {
    window.location.replace(route)
}


function requestAPI(endpoint, method, body, callback) {

    //console.log(body)
    let settings = {
        "url": "http://localhost:5000/api" + endpoint,
        "method": method,
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": jwtToken
        },
        "data": body,
        "success": callback,
        "error": ((error) => {
            if (error.status == 401) {
                //route('/');
            } else if (error.status == 404) {
                route('/')
            }
        })
    };

    return $.ajax(settings).done();
}

function logout() {
    deleteAllCookies();
    serverLogout((() => {
        route('/');
    }));
}

function tokenExpired() {
    if (!jwtToken) {
        return true;
    }

    let exp = JSON.parse(atob(jwtToken.replace('Bearer ', '').split('.')[1])).exp - Math.ceil(((new Date().getTime()) / 1000))
    if (exp > 0) {
        return false;
    } else {
        return true;
    }
}

function cookiesExpired() {
    let cookies = {}
    document.cookie.split(';').forEach((cookie) => {
        let re = /[=]+/;
        if (cookie.length == 0) {
            return
        }
        let index = cookie.match(re).index

        if (parseInt(cookie.substring(index + 1, cookie.length))) {
            cookies[cookie.substring(0, index).replace(' ', '')] = parseInt(cookie.substring(index + 1, cookie.length));
        } else {
            cookies[cookie.substring(0, index).replace(' ', '')] = cookie.substring(index + 1, cookie.length);
        }
    });
    if (!cookies.hasOwnProperty('exp')) {
        return true;
    }
    let exp = cookies.exp - Math.ceil(((new Date().getTime()) / 1000))
    if (exp > 0) {
        return false;
    } else {
        return true;
    }
}

function getCookies() {
    let cookies = {}
    document.cookie.split(';').forEach((cookie) => {
        let re = /[=]+/;
        if (cookie.length == 0) {
            return
        }
        let index = cookie.match(re).index

        if (parseInt(cookie.substring(index + 1, cookie.length))) {
            cookies[cookie.substring(0, index).replace(' ', '')] = parseInt(cookie.substring(index + 1, cookie.length));
        } else {
            cookies[cookie.substring(0, index).replace(' ', '')] = cookie.substring(index + 1, cookie.length);
        }
    });
    return cookies;
}

function deleteAllCookies() {
    var cookies = document.cookie.split(";");

    for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i];
        var eqPos = cookie.indexOf("=");
        var name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
}