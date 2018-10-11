if (text.match("^/")) {
    // parameter: [string]
    submit_command(text.substr(1).split(' '));
    // user: dict, timestamp: int, text: string, private: bool
    display_message(current_user, current_timestamp, text.substr(1), true);
} else if (text.match("^image:")) {
    // image: string, width: int, height: int
    submit_image(text.substr(6), 300, 300);
    // user: dict, timestamp: int, image: string, width: int, height: int, private: bool
    display_image(current_user, current_timestamp, text.substr(6), 300, 300, false);
} else {
    // text: string
    submit_command(["intercept", text]);
    // user: dict, timestamp: int, text: string, private: bool
    display_message(current_user, current_timestamp, text, false);
}
