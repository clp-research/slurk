if (data.html) {
    display_message(data.user, data.timestamp, markdown.makeHtml(data.message), data.private, true);
} else {
    display_message(data.user, data.timestamp, data.msg, data.private, false);
}
