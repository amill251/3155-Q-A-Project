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
        response.data.forEach(question => {
            console.log(question.contents);
            $('.question-title').html(question.title);
            $('#question-body').html(question.contents);
            $('.q-timestamp').html(question.date_created);
        });
    }, location.search)
}