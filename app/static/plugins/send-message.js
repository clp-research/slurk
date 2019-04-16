if (text.match("^/")) {
    submit_command(text.substr(1).split(' '));
    display_message(current_user, current_timestamp, text.substr(1), true);
} else if (text.match("^image:")) {
    submit_image(text.substr(6), 300, 300, () => {
        display_image(current_user, current_timestamp, text.substr(6), 300, 300, false);
    }, (error) => {
        display_image(current_user, current_timestamp, text.substr(6), 300, 300, true);
        if (error === undefined) {
            unknown_error(current_timestamp);
        } else if (error === "insufficient rights") {
            display_info(current_timestamp, "You are not allowed to send an image");
        } else {
            display_info(current_timestamp, error);
        }
    });
} else {
    submit_text(text, () => {
        display_message(current_user, current_timestamp, text, false);
    }, (error) => {
        display_message(current_user, current_timestamp, text, true);
        if (error === undefined) {
            unknown_error(current_timestamp);
        } else if (error === "insufficient rights") {
            display_info(current_timestamp, "You are not allowed to send a message");
        } else {
            display_info(current_timestamp, error);
        }
    });
}
