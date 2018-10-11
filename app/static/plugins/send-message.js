if (text.match("^/")) {
    // room, parameter
    submit_command(current_room, text.substr(1).split(' '));
    // user, time, command, private
    display_message(current_user, current_timestamp, text.substr(1), true);
} else if (text.match("^image:")) {
    // room, image, width, height
    submit_image(current_room, text.substr(6), 300, 300);
    // user, time, image, width, height, private
    display_image(current_user, current_timestamp, text.substr(6), 300, 300, false);
} else {
    // room, text
    submit_text(current_room, text);
    // user, time, text, private
    display_message(current_user, current_timestamp, text, false);
}
