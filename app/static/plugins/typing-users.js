delete users[self_user.id];

var users = Object.keys(users).map(function (key) {
    return users[key];
});

let typing_users = users.join(", ");

if (users.length == 0) {
    $("#typing").text("");
} else if (users.length == 1) {
    $("#typing").text(users[0] + " is typing");
} else if (users.length == 2) {
    $("#typing").text(users.join(" and ") + " are typing");
} else {
    $("#typing").text(users.join(", ") + " are typing");
}
