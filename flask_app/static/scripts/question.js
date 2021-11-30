$(document).ready(() => {
    refreshAuth((response) => {
        jwtToken = response.token;
    });
});

function submitPost() {
    let title = $('#title-subject-post').val();
    let questionContents = $('#question-contents').val();
    let userId = getCookies().user_id;

    let postBody = {
        "user_id": userId,
        "title": title,
        "contents": questionContents
    }

    createQuestion(postBody, ((response) => {
        if (response.succeed) {
            window.location.replace("feed");
        } else {
            alert('There was an error with this Question.')
        }
    }));

}