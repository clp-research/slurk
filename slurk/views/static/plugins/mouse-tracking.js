// the tracking area should have a fixed size in px
// padding and border-width but not margin will count as part of the area
let trackingArea = "tracking-area"

let mousePointer = {
    isMoving: false,
    pos: {x: undefined, y: undefined}
};

function getPosition (evt, area) {
    let elem = document.getElementById(area);
    let position = elem.getBoundingClientRect();
    mousePointer.pos.x = (evt.clientX - position.left) / position.width;
    mousePointer.pos.y = (evt.clientY - position.top) / position.height;
}

function emitPosition(area) {
    if (mousePointer.isMoving) {
        console.log(mousePointer.pos)
        socket.emit("mouse", {
           type: "move",
           coordinates: mousePointer.pos,
           element_id: area,
           room: self_room
	});
        mousePointer.isMoving = false;
    }
}

function trackMovement(area, interval) {
    $("#" + area).mousemove(function(e) {
        getPosition(e, area);
        mousePointer.isMoving = true;
    });
    setInterval(emitPosition, interval, area);
}

function trackClicks(area) {
    $("#" + area).click(function(e) {
	console.log('You clicked.');
        getPosition(e, area);
        socket.emit("mouse", {
            type: "click",
            coordinates: mousePointer.pos,
            element_id: area,
            room: self_room
        });
    });
}

// get position within trackingArea every 100 ms
trackMovement(trackingArea, 100);
trackClicks(trackingArea);
