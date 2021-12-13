$(document).ready(() => {
    refreshAuth((response) => {
        jwtToken = response.token;
        loadQuestion();
    });
});

function loadQuestion() {

    //console.log(location.search);

    getQuestion((response) => {
        //console.log(response);
        questionId = response.data[0].question_id;
        userId = response.data[0].user_id;

        if(userId != getCookies().user_id) {
            route('/');
        }

        $('#title-subject-post').val(response.data[0].title)
        $('#question-contents').text(response.data[0].contents)
        
        $('#submit-edit').click(() => {
            submitEdit(questionId);
        })
    }, location.search)
}

function submitEdit(questionId) {
    let title = $('#title-subject-post').val()
    let questionContents = $('#question-contents').val()
    let postBody = {
        "question_id" : questionId,
        "user_id" : getCookies().user_id,
        "title" : title,
        "contents" : questionContents
    }

    postQuestionEdit(() => {
        route('/view-question?question=' + questionId)
    }, postBody)
}