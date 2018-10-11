if (text.match("^/")) {
    submit_command(text.substr(1).split(' '));
    display_message(current_user, current_timestamp, text.substr(1), true);
} else {
    submit_command(["intercept", text]);
    display_message(current_user, current_timestamp, text, false);
}
