$(document).ready(() => {
    loadPosts()
});

function loadPosts() {
    getQuestions((response) => {
        console.log(response)
        response.data.forEach(questionResponse => {
            $('#feed-container').append(createHTMLPostTemplate(questionResponse));
        });
    })

}


function createHTMLPostTemplate(questionData) {
    console.log(questionData);
    let datetime = (new Date(questionData.date_created)).toLocaleString()
    let post = `
    <div class="d-flex justify-content-center row my-2">
    <div class="col-md-8">
    <div class="d-flex flex-column comment-section" id="myGroup" style="box-shadow: 0 2px 4px 0px rgba(0,0,0,0.16);">
        <div class="bg-white p-2">
        <div class="d-flex flex-row user-info">
            <div class="d-flex flex-column justify-content-start ml-2"><span
                class="d-block font-weight-bold name">` + questionData.title + `</span><span class="date text-black-50">Shared
                publicly - ` + datetime + `</span></div>
        </div>
        <div class="mt-2">
            <p class="comment-text">` + questionData.contents + `</p>
        </div>
        </div>
        <div class="bg-white p-2">
        <div class="d-flex flex-row fs-12">
            <div class="like p-2 cursor"><i class="fa fa-thumbs-o-up"></i><span class="ml-1">Like</span></div>
            <div class="like p-2 cursor action-collapse" data-toggle="collapse" aria-expanded="true"
            aria-controls="collapse-1" href="#collapse-1"><i class="fa fa-commenting-o"></i><span
                class="ml-1">Comment</span></div>
            <div class="like p-2 cursor action-collapse" data-toggle="collapse" aria-expanded="true"
            aria-controls="collapse-2" href="#collapse-2"><i class="fa fa-share"></i><span class="ml-1">Share</span>
            </div>
        </div>
        </div>
        <div id="collapse-1" class="bg-light p-2 collapse" data-parent="#myGroup">
        <div class="d-flex flex-row align-items-start"><img class="rounded-circle"
            src="https://i.imgur.com/RpzrMR2.jpg" width="40"><textarea
            class="form-control ml-1 shadow-none textarea"></textarea></div>
        <div class="mt-2 text-right"><button class="btn btn-primary btn-sm shadow-none" type="button">Post
            comment</button><button class="btn btn-outline-primary btn-sm ml-1 shadow-none"
            type="button">Cancel</button></div>
        </div>
        <div id="collapse-2" class="bg-light p-2 collapse" data-parent="#myGroup">
        <div class="d-flex flex-row align-items-start"><i class="fa fa-facebook border p-3 rounded mr-1"></i><i
            class="fa fa-twitter border p-3 rounded mr-1"></i><i
            class="fa fa-linkedin border p-3 rounded mr-1"></i><i
            class="fa fa-instagram border p-3 rounded mr-1"></i><i
            class="fa fa-dribbble border p-3 rounded mr-1"></i> <i
            class="fa fa-pinterest-p border p-3 rounded mr-1"></i> </div>
        </div>
    </div>
    </div>
    </div>
    `
    return post;
}