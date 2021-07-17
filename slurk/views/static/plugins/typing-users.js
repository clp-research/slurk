let typing_users = Object.values(users);

if (typing_users.length === 0) {
    $("#typing").text("");
} else if (typing_users.length === 1) {
    $("#typing").html("<em>" + typing_users[0] + "</em> is typing ...");
} else if (typing_users.length === 2) {
    $("#typing").html("<em>" + typing_users.join("</em> and <em>") + "</em> are typing ...");
} else {
    $("#typing").html("<em>" + typing_users.join("</em>, <em>") + "</em> are typing ...");
}
