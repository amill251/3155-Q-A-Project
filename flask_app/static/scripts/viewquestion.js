$(document).ready(() => {
    let cookies = getCookies();
    refreshAuth((response) => {
        jwtToken = response.token;
        loadQuestion();
    });
});

function loadQuestion() {

    console.log(location.search);

    getQuestion((response) => {
        console.log(response);
        questionId = response.data[0].question_id;
        userId = response.data[0].user_id;

        if(userId == getCookies().user_id) {
            $('#delete-button').show();
            $('#delete-button').click(() => {
                deleteQuestion(questionId);
            })
            $('#edit-button').show();
            $('#edit-button').click(() => {
                editQuestion(questionId);
            })
        }
        response.data.forEach(question => {
            console.log(question)
            console.log(question.contents);
            $('.question-title').html(question.title);
            $('#question-body').html(question.contents);
            $('.q-timestamp').html(question.date_created);
            $('#user-asks').text(question.username + ' asks: ')
        });
    }, location.search)
}

function deleteQuestion(questionId) {
    let questionBody = {
        'delete' : questionId
    }

    postQuestionDelete(() => {
        route('/');
    }, questionBody);
}

function editQuestion(questionId) {
    route('/edit-question?question=' + questionId);
}