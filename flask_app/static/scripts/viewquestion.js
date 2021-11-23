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
            console.log(question)
            // $('#feed-container').append(createHTMLPostTemplate(questionResponse));
        });
    }, location.search)
}