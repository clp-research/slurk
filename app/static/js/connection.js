let socket;
let startTime;
let ping_pong_times = [];
let users = {};
let is_typing = -1;

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
    $(".fade").fadeOut(null, () => {
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
        if (layout.subtitle !== "") {
            $("#subtitle").text(layout.subtitle);
        }
    }).fadeIn();
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
        if (user_id !== self_user.id)
            current_users += users[user_id] + ', ';
    }
    $('#current-users').text(current_users + "You");
}

$(document).ready(() => {
    socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    window.setInterval(function () {
        startTime = (new Date).getTime();
        socket.emit("my_ping", { "typing": is_typing });
        updateUsers();
        if (is_typing !== -1) {
            is_typing += 1;
        }
    }, 1000);

    socket.on("pong", (data) => {
        $("#ping").text(data);
    });

    socket.on('joined_room', (data) => {
        self_room = data.room.name;
        apply_room_properties(data.room);
        apply_layout(data.layout);
        socket.emit('get_user', null, (success, user) => {
            if (verify_query(success, user)) {
                self_user = user;
                for (let user_id in data.room.current_users) {
                    if (Number(user_id) !== user.id)
                        users[user_id] = data.room.users[user_id];
                }
                updateUsers();
            }
        });
    });

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