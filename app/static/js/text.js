let typing = {};
let update_typing = undefined;
let keypress = undefined;
let incoming_message = undefined;
let is_typing = -1;

$(document).ready(() => {
    socket.on("message", function (data) {
        if (incoming_message !== undefined && data.user.id !== self_user.id) {
            incoming_message(data)
        }
    });

    socket.on('start_typing', function (data) {
        if (data.user.id === self_user.id) {
            return
        }
        typing[data.user.id] = data.user.name;
        if (update_typing !== undefined) {
            update_typing(typing);
        }
    });

    socket.on('stop_typing', function (data) {
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
        if (is_typing === 3)
            socket.emit("keypress", { "typing": false });
    }, 1000);

    $('#text').keypress(function(e) {
        if (keypress === undefined || $('#text').is('[readonly]')) {
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
            $(e.target).val('');
            if (text === '') {
                return
            }
            is_typing = -1;
            let date = new Date();
            let time = date.getTime() - date.getTimezoneOffset() * 60000;
            keypress(self_room, self_user, time / 1000, text);
        }
    });
});