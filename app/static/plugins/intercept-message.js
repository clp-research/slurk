if (text.match("^/")) {
    submit_command(current_room, text.substr(1).split(' '));
    display_message(current_user, current_timestamp, text.substr(1), true);
} else {
    submit_command(current_room, ["intercept", text]);
    display_message(current_user, current_timestamp, text, false);
}
