function _append(text) {
    $('#chat-area').append(text);
    let content = $('#content');
    content.animate({ scrollTop: content.prop("scrollHeight") }, 0);
}

function _getTime(timestamp) {
    let currentDate = undefined
    if (typeof timestamp === "string") {
        currentDate = new Date(timestamp.replace(" ", "T"))
        currentDate.setTime(currentDate.getTime() - new Date().getTimezoneOffset() * 60000)
    } else if (timestamp === null) {
        currentDate = new Date()
    } else {
        currentDate = new Date((timestamp + new Date().getTimezoneOffset() * 60) * 1000);
    }
    return currentDate.getHours() + ":" + (currentDate.getMinutes() < 10 ? "0" + currentDate.getMinutes() : "" + currentDate.getMinutes());
}

function display_message(user, time, message, privateMessage, html = false) {
    if (self_user === undefined) {
        return;
    }

    let classes = "";
    if (Number(self_user.id) === Number(user.id)) {
        classes += "self";
    } else {
        classes += "other";
    }

    if (privateMessage) {
        classes += " private";
    }
    let text = $(
        "<li class='" + classes + "'>" +
        "  <div class='message-box'>" +
        "    <div>" +
        "      <span class='user'></span>" +
        "      <time></time>" +
        "    </div>" +
        "    <span class='message'></span>" +
        "  </div>" +
        "</li>");
    text.find(".user").text(self_user.id === user.id ? "You" : user.name);
    if (html) {
        text.find(".message").html(message);
    } else {
        text.find(".message").text(message);
    }
    text.find("time").text(_getTime(time));
    _append(text);
}

function display_image(user, time, url, width, height, privateMessage) {
    if (self_user === undefined) {
        return;
    }

    let classes = "";
    if (Number(self_user.id) === Number(user.id)) {
        classes += "self";
    } else {
        classes += "other";
    }
    if (privateMessage) {
        classes += " private";
    }

    if (width !== null) {
        width = parseInt(width);
    } else {
        width = 200;
    }
    if (height !== null) {
        height = parseInt(height);
    } else {
        height = 200;
    }

    let text = $(
        "<li class='" + classes + "'>" +
        "  <div class='message-box'>" +
        "    <div>" +
        "      <span class='user'></span>" +
        "      <time></time>" +
        "    </div>" +
        "    <img/>" +
        "  </div>" +
        "</li>");
    text.find(".user").text(self_user.id === user.id ? "You" : user.name);
    text.find("time").text(_getTime(time));
    text.find("img").attr("src", url).attr("width", width).attr("height", height);
    _append(text);
}

function display_info(time, message) {
    let text = $(
        "<li class='notification'>" +
        "  <p class='message'></p>" +
        "  <time></time>" +
        "</li>");
    text.find(".message").text(message);
    text.find("time").text(_getTime(time));
    _append(text);
}

function unknown_error(time) {
    let text = $(
        "<li class='notification'>" +
        "  <p class='message'></p>" +
        "  <time></time>" +
        "</li>");
    text.find(".message").html('An unknown error occurred.<br \>Please feel free to <a href="https://github.com/clp-research/slurk/issues/new">file the bug<\a>');
    text.find("time").text(_getTime(time));
    _append(text);
}

function submit_text(text, resolve, reject) {
    socket.emit('text', { room: self_room, message: text }, (success, error) => {
        if (verify_query(success, error)) {
            if (resolve !== undefined)
                resolve();
        } else {
            if (reject !== undefined) {
                reject(error);
            }
        }
    });
}

function submit_private_text(receiver, text, resolve, reject) {
    socket.emit('text', { room: self_room, receiver_id: receiver, message: text }, (success, error) => {
        if (verify_query(success, error)) {
            if (resolve !== undefined)
                resolve();
        } else {
            if (reject !== undefined) {
                reject(error);
            }
        }
    });
}

function submit_image(url, width, height, resolve, reject) {
    socket.emit('image', { room: self_room, url: url, width: width, height: height }, (success, error) => {
        if (verify_query(success, error)) {
            if (resolve !== undefined)
                resolve();
        } else {
            if (reject !== undefined) {
                reject(error);
            }
        }
    });
}

function submit_private_image(receiver, url, width, height, resolve, reject) {
    socket.emit('image', { room: self_room, receiver_id: receiver, url: url, width: width, height: height }, (success, error) => {
        if (verify_query(success, error)) {
            if (resolve !== undefined)
                resolve();
        } else {
            if (reject !== undefined) {
                reject(error);
            }
        }
    });
}

function submit_command(command, resolve, reject) {
    socket.emit('message_command', { room: self_room, command: command }, (success, error) => {
        if (verify_query(success, error)) {
            if (resolve !== undefined)
                resolve();
        } else {
            if (reject !== undefined) {
                reject(error);
            }
        }
    });
}
