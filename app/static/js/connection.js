let socket;
let users = {};

let self_user = undefined;
let self_room = undefined;

function apply_user_permissions(permissions) {
    $('#type-area').fadeTo(null, permissions.message.text || permissions.message.image || permissions.message.command);
}

function apply_room_properties(room) {
    if (room.read_only) {
        $('#text').prop('readonly', true).prop('placeholder', 'This room is read-only');
    } else {
        $('#text').prop('readonly', false).prop('placeholder', 'Enter your message here!');
    }

    $('#user-list').fadeTo(null, room.show_users);
    $('#latency').fadeTo(null, room.show_latency);
}

function apply_layout(layout) {
    if (!layout)
        return;
    if (layout.html !== "") {
        $("#sidebar").html(layout.html);
    }
    if (layout.css !== "") {
        $("#custom-styles").html(layout.css);
    }
    if (layout.script !== "") {
        window.eval(layout.script);
    }
    if (layout.title !== "") {
        document.title = layout.title;
    } else {
        document.title = 'Slurk';
    }
    $("#title").text(document.title);
    $("#subtitle").text(layout.subtitle);
}

function verify_query(success, message) {
    if (!success) {
        if (message === "invalid session id") {
            // Reload page if user is not logged in
            window.location.reload();
        } else {
            console.error(message)
        }
        return false;
    }
    return true;
}

function updateUsers() {
    let current_users = "";
    for (let user_id in users) {
        current_users += users[user_id] + ', ';
    }
    $('#current-users').text(current_users + "You");
}

function headers(xhr) {
    xhr.setRequestHeader ("Authorization", "Token " + TOKEN);
}

$(document).ready(() => {
    let uri = location.protocol + '//' + document.domain + ':' + location.port + "/api/v2";
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    socket.on("pong", (data) => {
        $("#ping").text(data);
    });

    async function joined_room(data) {
        self_room = data['room'];

        let room_request = $.get({ url: uri + "/room/" + data['room'], beforeSend: headers });
        let user_request = $.get({ url: uri + "/user/" + data['user'], beforeSend: headers });
        let history = $.get({ url: uri + "/user/" + data['user'] + "/logs", beforeSend: headers });

        let room = await room_request;
        let layout = $.get({ url: uri + "/layout/" + room.layout, beforeSend: headers });
        apply_room_properties(room);

        let user = await user_request;
        self_user = { id: user.id, name: user.name };

        users = {};
        for (let user_id in room.current_users) {
            if (Number(user_id) !== self_user.id)
                users[user_id] = room.current_users[user_id];
        }

        updateUsers();
        apply_layout(await layout);
        history = await history;
        console.log(history[room.name]);
        print_history(history[room.name]);

    }

    async function left_room(data) {}

    socket.on('joined_room', joined_room);
    socket.on('left_room', left_room);

    socket.on('connect', (data) => {
        socket.emit("get_user_permissions", null, (success, permissions) => {
            if (verify_query(success, permissions)) {
                apply_user_permissions(permissions);
            }
        });
    });

    socket.on('status', function (data) {
        if (typeof self_user === "undefined")
            return;
        switch (data.type) {
            case "join":
                let user = data.user;
                updateUsers();
                break;
            case "leave":
                delete users[data.user.id];
                updateUsers();
                break;
        }
    });

    socket.emit("ready")
});