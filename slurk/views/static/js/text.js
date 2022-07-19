let typing = {};
let update_typing = undefined;
let keypress = undefined;
let incoming_text = undefined;
let incoming_image = undefined;
let is_typing = -1;

$(document).ready(() => {
    socket.on("text_message", function (data) {
        if (self_user === undefined) {
            return;
        }
        if (incoming_text !== undefined && data.user.id !== self_user.id) {
            incoming_text(data)
        }
    });

    socket.on("image_message", function (data) {
        if (self_user === undefined) {
            return;
        }
        if (incoming_image !== undefined && data.user.id !== self_user.id) {
            incoming_image(data)
        }
    });

    socket.on("start_typing", function (data) {
        if (self_user === undefined) {
            return;
        }
        if (data.user.id === self_user.id) {
            return
        }
        typing[data.user.id] = data.user.name;
        if (update_typing !== undefined) {
            update_typing(typing);
        }
    });

    socket.on("stop_typing", function (data) {
        if (self_user === undefined) {
            return;
        }
        if (data.user.id === self_user.id) {
            return
        }
        delete typing[data.user.id];
        if (update_typing !== undefined) {
            update_typing(typing);
        }
    });

    window.setInterval(function () {
        if (is_typing !== -1)
            is_typing += 1;
        if (is_typing === 3) {
            socket.emit("keypress", { "typing": false });
            is_typing = -1;
	}
    }, 1000);


    $("#text").keypress(function (e) {
        if (keypress === undefined || $("#text").is("[readonly]")) {
            return;
        }
        if (is_typing === -1) {
            socket.emit("keypress", { "typing": true });
        }
        is_typing = 0;
        let code = e.keyCode || e.which;
        // 13: RETURN key
        if (code === 13) {
            let text = $(e.target).val();
            $(e.target).val("");
            if (text === "") {
                return
            }
            is_typing = -1;
            let date = new Date();
            let time = date.getTime() - date.getTimezoneOffset() * 60000;
            keypress(self_room, self_user, time / 1000, text);
        }
    });
});
