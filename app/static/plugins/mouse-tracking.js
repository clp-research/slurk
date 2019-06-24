let trackingArea = "#current-image";
let mouse = {
    move: false,
    pos: {x:false, y:false}
};

function getPosition (evt, area) {
    position = $(area).offset();
    mouse.pos.x = evt.clientX - position.left;
    mouse.pos.y = evt.clientY - position.top;
}

function emitPosition(a) {
    if (mouse.move) {
        socket.emit('mousePosition', {
            type:'move',
            coordinates:mouse.pos,
            element:a,
            room:self_room
        });
        mouse.move = false;
    }
}

function trackMovement(area,interval) {
    $(area).mousemove(function(e){
        getPosition(e, area);
        mouse.move = true;
    });
    setInterval(emitPosition,interval,area)
}

// get position within trackingArea every 100 ms
trackMovement(trackingArea, 100);
