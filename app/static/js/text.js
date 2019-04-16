let typing = {};
let update_typing = undefined;
let keypress = undefined;
let incoming_message = undefined;

$(document).ready(() => {
    socket.on("message", function (data) {
        console.log("message", data);
        if (incoming_message !== undefined && data.sender.id !== self_user.id) {
            incoming_message(data)
        }
    });

    socket.on('start_typing', function (data) {
        typing[data.sender.id] = data.sender.name;
        if (update_typing !== undefined) {
            update_typing(typing);
        }
    });

    socket.on('stop_typing', function (data) {
        delete typing[data.sender.id];
        if (update_typing !== undefined) {
            update_typing(typing);
        }
    });

    $('#text').keypress(function(e) {
        if (keypress === undefined || $('#text').is('[readonly]')) {
            return;
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