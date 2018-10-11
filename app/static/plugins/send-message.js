if (text.match("^/")) {
    submit_command(current_room, text.substr(1).split(' '));
} else if (text.match("^http")) {
    submit_image(current_room, text, 300, 300);
} else {
    submit_text(current_room, text);
}