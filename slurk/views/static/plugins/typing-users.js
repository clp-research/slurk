let typing_users = Object.values(users);

let info_text = $(
    "<li class='other'>" +
    "  <div class='message-box'>" +
    "    <div class='dot-flashing'></div>" +
    "    <span class='message'></span>" +
    "  </div>" +
    "</li>");


if (typing_users.length === 0) {
    $("#typing").text("");
} else {
    if (typing_users.length === 1) {
        info_text.find(".message").html("<em>" + typing_users[0] + "</em> is typing ...");
    } else if (typing_users.length === 2) {
        info_text.find(".message").html("<em>" + typing_users.join("</em> and <em>") + "</em> are typing ...");
    } else {
        info_text.find(".message").html("<em>" + typing_users.join("</em>, <em>") + "</em> are typing ...");
    }
    $("#typing").html(info_text);

    let content = $('#content');
    content.animate({ scrollTop: content.prop("scrollHeight") }, 0);
}

