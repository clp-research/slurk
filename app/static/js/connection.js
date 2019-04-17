let socket;
let startTime;
let ping_pong_times = [];
let users = {};
let is_typing = -1;

let self_user = undefined;
let self_room = undefined;

function apply_user_permissions(permissions) {
    if (permissions.message.text || permissions.message.image || permissions.message.command) {
        $('#type-area').show();
    }
}

function apply_room_properties(room) {
    if (room.read_only) {
        $('#text').prop('readonly', true).prop('placeholder', 'This room is read-only');
    } else {
        $('#text').prop('readonly', false).prop('placeholder', 'Enter your message here!');
    }
    if (room.show_users) {
        $('#user-list').show();
    }
    if (room.show_latency) {
        $('#latency').show();
    }
}

function apply_layout(layout) {
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
    if (layout.subtitle !== "") {
        $("#subtitle").text(layout.subtitle);
    }
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
    let current_users = "You";
    for (let user_id in users) {
        if (user_id !== self_user.id)
            current_users += ", " + users[user_id];
    }
    $('#current-users').text(current_users);
}

$(document).ready(() => {
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    window.setInterval(function () {
        startTime = (new Date).getTime();
        socket.emit("my_ping", { "typing": is_typing });
        if (is_typing !== -1) {
            is_typing += 1;
        }
    }, 1000);

    socket.on("my_pong", function () {
        let latency = (new Date).getTime() - startTime;
        ping_pong_times.push(latency);
        ping_pong_times = ping_pong_times.slice(-5);
        let sum = 0;
        for (let i = 0; i < ping_pong_times.length; ++i)
            sum += ping_pong_times[i];
        let ping = $("#ping");
        ping.text(Math.round(10 * sum / ping_pong_times.length) / 10);
    });

    socket.on('connect', (data) => {
        socket.emit("get_user", null, (success, user) => {
            if (verify_query(success, user)) {
                self_user = user;
                updateUsers();
            }
        });
        socket.emit('get_rooms_by_user', null, (success, rooms) => {
            if (verify_query(success, rooms)) {
                let room = rooms[0];
                if (room) {
                    self_room = room.name;
                    apply_room_properties(room);
                    for (let user_id in room.current_users) {
                        if (Number(user_id) !== self_user.id)
                            users[user_id] = room.users[user_id];
                    }
                    updateUsers();
                }
            }
        });
        socket.emit("get_layouts_by_user", null, (success, layouts) => {
            if (verify_query(success, layouts)) {
                let room = Object.keys(layouts)[0];
                if (room && layouts[room]) {
                    apply_layout(layouts[room]);
                }
            }
        });
        socket.emit("get_permissions_by_user", null, (success, permissions) => {
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
                if (user.id !== self_user) {
                    users[user.id] = user.name;
                    updateUsers();
                }
                break;
            case "leave":
                delete users[data.user.id];
                updateUsers();
                break;
        }
    });
});