let old_value = "";
let typed_messages = {};


function showMessagePreview(data) {
    if (self_user === undefined || data.user.id === self_user.id) {
        return;
    }

    let scrollbar_at_bottom = false;
    let content = $('#content');
    if (content.prop("scrollTop") + content.prop("clientHeight") + 20 >= content.prop("scrollHeight")) {
        scrollbar_at_bottom = true;
    }

    if (data.text == "") {
        delete typed_messages[data.user.name];
    } else {
        typed_messages[data.user.name] = data.text;
    }

    $("#typing").empty();
    for (let user_name in typed_messages) {
        let bubble = $(
        "<li class='other'>" +
        "  <div class='message-box'>" +
        "    <div class='dot-flashing'></div>" +
        "    <span class='message'>" + user_name + "</span>" +
            "    <div>" + typed_messages[user_name] + "</div>" +  
        "  </div>" +
        "</li>");
        $("#typing").append(bubble);
    }
    // only scroll down, if user not looking through older history
    if (scrollbar_at_bottom) {
        content.animate({ scrollTop: content.prop("scrollHeight") }, 0);
    }
}

// at some point the user should submit the message
// in order not to encourage them to communicate only
// via the message preview, deleting and changing messages is disabled
function updateMessage() {
    let new_value = $("#text").val();

    if (old_value.length >= new_value.length) {
        $("#text").val(old_value);
        alert("You may not edit a typed message.");
    } else {
        old_value = new_value;
        socket.emit("typed_message", {
            "text": old_value
        });
    }
}

function submitMessage(event) {
    let code = event.keyCode || event.which;
    if (code === 13) {
        old_value = "";
        socket.emit("typed_message", {
            "text": old_value
        });
    }
}

function submitMessageOnInactivity(data) {
    if (self_user === undefined || keypress === undefined) {
        return;
    }
    if (data.user.id === self_user.id) {
        if (old_value !== "") {
            let date = new Date();
            let time = date.getTime() - date.getTimezoneOffset() * 60000;
            keypress(self_room, self_user, time / 1000, old_value);

            old_value = "";
            $("#text").val("");
        }
    } else {
        data.text = "";
        showMessagePreview(data);
    }
}


$("#text").on("keypress", submitMessage);
$("#text").on("input", updateMessage);

socket.on("typed_message", showMessagePreview);
socket.on("stop_typing", submitMessageOnInactivity);

socket.on('left_room', function removeHandlers() {
    $("#text").off("keypress", submitMessage);
    $("#text").off("input", updateMessage);

    socket.off("typed_message", showMessagePreview);
    socket.off("stop_typing", submitMessageOnInactivity);
    socket.off("left_room", removeHandlers);
});
