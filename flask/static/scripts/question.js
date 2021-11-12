callback = function (data) {
    //TODO
    console.log(data);
    if (data.succeed) {
        window.location.replace("feed");
    }
    else {
        console.log(data.message);
    }
    //if success = false, let user know the error (either password or user invalid)
}