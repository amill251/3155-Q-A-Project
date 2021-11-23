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

        if(response.data[0].user_id == getCookies().user_id) {
            $('#delete-button').show();
            $('#delete-button').click(() => {
                deleteQuestion(response.data[0].question_id);
            })
        }
        response.data.forEach(question => {
            console.log(question)
            console.log(question.contents);
            $('.question-title').html(question.title);
            $('#question-body').html(question.contents);
            $('.q-timestamp').html(question.date_created);
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