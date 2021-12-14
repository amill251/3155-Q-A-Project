$(document).ready(() => {
    let cookies = getCookies();

    $('#user-profile').text('Welcome Back ' + cookies.user);
    refreshAuth((response) => {
        jwtToken = response.token;
        loadPosts();
    });
});

function loadPosts() {
    getQuestions((response) => {
        response.data.sort((a, b) => {
            timeA = (new Date(a.date_created)).getTime();
            timeB = (new Date(b.date_created)).getTime();
            return timeB - timeA;
        }).forEach(questionResponse => {
            $('#feed-container').append(createHTMLPostTemplate(questionResponse));
        });
    }, location.search)
}


function createHTMLPostTemplate(questionData) {

    let datetime = (new Date(questionData.date_created)).toLocaleString()
    let post = `
    <div class="d-flex justify-content-center row my-2">
    <div class="col-md-8">
    <div class="d-flex flex-column comment-section" id="myGroup" style="box-shadow: 0 2px 4px 0px rgba(0,0,0,0.16);">
        <div class="bg-white p-2">
        <div class="d-flex flex-row user-info">
        <a href="view-question?question=` + questionData.question_id + `">
            <div class="d-flex flex-column justify-content-start ml-2"><span
                class="d-block font-weight-bold name">` + questionData.title + `</span><span class="date text-black-50">` + questionData.username + `
                 - ` + datetime + `</span></div></a>
        </div>
        <div class="mt-2">
            <p class="comment-text">` + questionData.contents + `</p>
        </div>
        </div>
    `
    return post;
}

function searchQuestion() {
    let search = $('#search-box').val();
    route("/feed?query=" + search)

}