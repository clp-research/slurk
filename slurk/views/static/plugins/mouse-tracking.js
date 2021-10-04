// the tracking area should have a fixed size in px
// padding and border-width but not margin will count as part of the area
let trackingArea = "tracking-area"

let trackMousePointer = {
    isMoving: false,
    pos: {x: undefined, y: undefined}
};

function trackGetPosition (evt, area) {
    let elem = document.getElementById(area);
    let position = elem.getBoundingClientRect();
    trackMousePointer.pos.x = (evt.clientX - position.left) / position.width;
    trackMousePointer.pos.y = (evt.clientY - position.top) / position.height;
}

function emitPosition(area) {
    if (trackMousePointer.isMoving) {
        socket.emit("mouse", {
           type: "move",
           coordinates: trackMousePointer.pos,
           element_id: area,
           room: self_room
	});
        trackMousePointer.isMoving = false;
    }
}

function trackMovement(area, interval) {
    $("#" + area).mousemove(function(e) {
        trackGetPosition(e, area);
        trackMousePointer.isMoving = true;
    });
    setInterval(emitPosition, interval, area);
}

function trackClicks(area) {
    $("#" + area).click(function(e) {
        trackGetPosition(e, area);
        socket.emit("mouse", {
            type: "click",
            coordinates: trackMousePointer.pos,
            element_id: area,
            room: self_room
        });
    });
}

// get position within trackingArea every 100 ms
trackMovement(trackingArea, 100);
trackClicks(trackingArea);
