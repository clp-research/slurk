let typing_users = Object.values(users);

if (typing_users.length === 0) {
    $("#typing").text("");
} else if (typing_users.length === 1) {
    $("#typing").text(typing_users[0] + " is typing");
} else if (typing_users.length === 2) {
    $("#typing").text(typing_users.join(" and ") + " are typing");
} else {
    $("#typing").text(typing_users.join(", ") + " are typing");
}
