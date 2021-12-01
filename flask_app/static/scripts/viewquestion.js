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
        $('#report-button').click(() => {
            reportQuestion(questionId);
        });
        console.log("------");
        console.log(response.data[0]);
        if (response.data[0].user_reported) {
            console.log("Made it inside print statement");
            $('#report-button').addClass("btn-reported");
            $('#report-button').text("Reported");
        }

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

function reportQuestion(questionId) {
    let reportBody = {
        "question_id": questionId,
        "answer_id": null
    }

    postQuestionReport(() => {
        location.reload();
    }, reportBody);
}

function reportAnswer(questionId, answerId) {
    let reportBody = {
        "question_id": questionId,
        "answer_id": answerId
    }

    postQuestionReport(() => {
        location.reload();
    }, reportBody);
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
        upvote = ' btn-vote-green'
        downvote = ' btn-vote-light'
    } else if (answerData.votes.uservotes == 'downvote') {
        upvote = ' btn-vote-light'
        downvote = ' btn-vote-red'
    } else {
        upvote = ' btn-vote-light'
        downvote = ' btn-vote-light'
    }
    let reportText = '';
    let reportClass ='';

    if (answerData.user_report) {
        reportText = 'Reported';
        reportClass = 'btn-reported';
    } else {
        reportText = 'Report Answer';
    }

    let answer = `
    <div class="card mb-3">
    <button class="btn btn-danger ` + reportClass + `" onclick="reportAnswer(` + answerData.question_id + ', ' + answerData.answer_id + `)">` + reportText + `</button>
        <div class="card-header">
            <div class="row">
                <div class="col-8">` + answerData.username + `</div>
                <div class="col-4 text-end">` + datetime + `</div>
            </div>
        </div>
        <div class="card-body d-flex">
            <div class="p-2"> 
                <div class="btn-vote p-1` + upvote + `" onclick="voteAnswer(` + answerData.answer_id + `,'upvote')">
                    <i class="fas fa-arrow-up" style="font-size: 20px;"></i>
                </div>
                <div style="height: 33.33%" class="p-1">
                    <div class="m-0 d-flex justify-content-center align-items-center" style="line-height: 1.25rem;">` + answerData.votes.total_votes + `</div>
                </div>
                <div class="btn-vote p-1` + downvote + `" onclick="voteAnswer( `+ answerData.answer_id + `,'downvote')">
                    <i class="fas fa-arrow-down" style="font-size: 20px;"></i>
                </div>
            </div>
            <div class="card mt-0 w-100">
                <div class="card-body">
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