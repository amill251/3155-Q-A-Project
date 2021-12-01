$(document).ready(() => {
    let cookies = getCookies();
    refreshAuth((response) => {
        jwtToken = response.token;
        loadQuestion();
        loadAnswers();
    });
});


function loadQuestion() {

    console.log(location.search);

    getQuestion((response) => {
        console.log(response);
        questionId = response.data[0].question_id;
        userId = response.data[0].user_id;

        if (userId == getCookies().user_id) {
            $('#delete-button').show();
            $('#delete-button').click(() => {
                deleteQuestion(questionId);
            });
            $('#edit-button').show();
            $('#edit-button').click(() => {
                editQuestion(questionId);
            });
        }

        $('#submit-answer').click(() => {
            submitAnswer(questionId);
        });
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
        'delete': questionId
    }

    postQuestionDelete(() => {
        route('/');
    }, questionBody);
}

function editQuestion(questionId) {
    route('/edit-question?question=' + questionId);
}

function submitAnswer(questionId) {
    let answerContents = $('#answer-question').val();

    let postBody = {
        "question_id": questionId,
        "contents": answerContents
    }

    createAnswer(postBody, ((response) => {
        if (response.succeed) {
            window.location.reload();
        } else {
            alert('There was an error with this Answer.')
        }
    }));

}

function loadAnswers() {
    console.log('Running Load Answers');
    getAnswers((response) => {
        console.log('Get answers callback');
        $('#answer-container').empty();
        console.log(response.data);
        response.data.sort((a,b) => {
            return b.votes.total_votes - a.votes.total_votes;
        }).forEach(answerResponse => {
            $('#answer-container').append(createHTMLAnswerTemplate(answerResponse));
        });

        console.log('Got to the end of the append');
    }, location.search)
    console.log('Finished Load Answers');
}

function createHTMLAnswerTemplate(answerData) {

    let datetime = (new Date(answerData.date_created)).toLocaleString();
    let upvote = '';
    let downvote = ''

    if (answerData.votes.uservotes == 'upvote') {
        upvote = ' btn-success'
        downvote = ' btn-light'
    } else if (answerData.votes.uservotes == 'downvote') {
        upvote = ' btn-light'
        downvote = ' btn-danger'
    } else {
        upvote = ' btn-light'
        downvote = ' btn-light'
    }

    let answer = `
    <div class="card mb-3">
        <button class="btn m-2` + upvote + `" onclick="voteAnswer(` + answerData.answer_id + `,'upvote')">Upvote</button>
        <button class="btn m-2` + downvote + `" onclick="voteAnswer( `+ answerData.answer_id + `,'downvote')">Downvote</button>
        <div><h3>` + answerData.votes.total_votes + `</h3></div>
        <div class="card-header">
            <div class="row">
                <div class="col-8">` + answerData.username + `</div>
                <div class="col-4 text-end">` + datetime + `</div>
            </div>
        </div>
        <div class="card-body">
            <div class="card mt-0">
                <div class="card-body" style="background-color: rgba(73, 167, 86, 0.329);">
                    ` + answerData.contents + `
                </div>
            </div>
        </div>
    </div>
    `
    return answer;
}

function voteAnswer(answer_id, vote) {
    let voteBody = {
        "answer_id": answer_id,
        "vote_name": vote
    }
    console.log('----------------------------------------');
    console.log(voteBody);
    postVote(location.reload(), voteBody);
}