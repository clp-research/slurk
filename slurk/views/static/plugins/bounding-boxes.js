// Note: padding and border-width but not margin will count as part of the area
let drawingArea = "drawing-area";
let drawingElem = document.getElementById(drawingArea);

$(drawingElem).wrap("<div id='img-wrapper' style='position:relative;'></div>");
let wrapper = document.getElementById("img-wrapper");

// used as drawing layer for rectangles that have been confirmed
let canvas = createCanvas();
// used as a temporary layer before a rectangle has been completed
let tempCanvas = createCanvas();

configureCanvas(tempCanvas);
configureCanvas(canvas);

let context = createContext(canvas);
let tempContext = createContext(tempCanvas);

let rectangles = [];

// most recently drawn rectangle
let rectangle = {
    left: null,
    top: null,
    right: null,
    bottom: null
};

// bundle mouse pointer properties
let mousePointer = {
    pos: {x: null, y: null},
    drag: false,
    drag_start: null
};

// get position of mouse pointer relative to canvas
function getPosition(evt) {
    let position = canvas.getBoundingClientRect();
    mousePointer.pos.x = (evt.clientX - position.left) / canvas.width;
    mousePointer.pos.y = (evt.clientY - position.top) / canvas.height;
}

// create canvas element
function createCanvas() {
    let canvas = document.createElement("canvas");
    canvas.style.position = "absolute";
    wrapper.appendChild(canvas);

    return canvas;
}

// fit canvas over html element
function configureCanvas(cnv) {
    cnv.width = drawingElem.clientWidth;
    cnv.height = drawingElem.clientHeight;
    cnv.style.left = drawingElem.offsetLeft + "px";
    cnv.style.top = drawingElem.offsetTop + "px";
}

// set context attributes such as line color
function createContext(cnv) {
    let context = cnv.getContext("2d");
    context.fillStyle = "rgba(255,0,0,0.2)";
    context.strokeStyle = "red";
    context.lineWidth = 2;

    return context;
}

// switch coordinates to match their names
// i.e. 'left' is left to 'right', 'top' is above 'bottom'
function normalizeRectangle() {
    if (rectangle.right < rectangle.left) {
        let temp = rectangle.right;
        rectangle.right = rectangle.left;
        rectangle.left = temp;
    }
    if (rectangle.top > rectangle.bottom) {
        let temp = rectangle.top;
        rectangle.top = rectangle.bottom;
        rectangle.bottom = temp;
    }
}

// return true if cursor position is on the drawn rectangle
function isPosOnRectangle() {
    normalizeRectangle();
    if (
        mousePointer.pos.x >= rectangle.left && mousePointer.pos.x <= rectangle.right
        && mousePointer.pos.y <= rectangle.bottom && mousePointer.pos.y >= rectangle.top
    ) {
        return true;
    } else {
        return false;
    }
}

// take drag start- and endpoint to create rectangle
function createRectangle(evt) {
    rectangle.left = mousePointer.drag_start.x;
    rectangle.top = mousePointer.drag_start.y;
    getPosition(evt);
    rectangle.right = mousePointer.pos.x;
    rectangle.bottom = mousePointer.pos.y;

    return rectangle;
}

// draw rectangle shape on canvas
function drawRectangle(cntx, rect) {
    cntx.beginPath();
    cntx.fillRect(
        rect.left * canvas.width,
        rect.top * canvas.height,
        (rect.right - rect.left) * canvas.width,
        (rect.bottom - rect.top) * canvas.height
    );
    cntx.rect(
        rect.left * canvas.width,
        rect.top * canvas.height,
        (rect.right - rect.left) * canvas.width,
        (rect.bottom - rect.top) * canvas.height
    );
    cntx.stroke();
}

$(document).ready(() => {
    drawingElem.onload = function(evt) {
        configureCanvas(tempCanvas);
        configureCanvas(canvas);
        tempContext = createContext(tempCanvas);
        context = createContext(canvas);
    };

    // triggered if the drawingElem does change its size in any way
    // it adapts the size of the canvas according to these changes
    if (ResizeObserver) {  // not available on IE
        let resize_ob = new ResizeObserver(function(entries) {
            configureCanvas(tempCanvas);
            configureCanvas(canvas);
            tempContext = createContext(tempCanvas);
            context = createContext(canvas);

            // redraw all rectangles
            for (let i in rectangles) {
                drawRectangle(context, rectangles[i]);
            }
        })
        resize_ob.observe(drawingElem);
    }

    wrapper.onmousedown = function(evt) {
        getPosition(evt);
        mousePointer.drag = true;
        mousePointer.drag_start = {x: mousePointer.pos.x, y: mousePointer.pos.y};
    };

    wrapper.onmouseup = function(evt) {
        mousePointer.drag = false;
    };

    wrapper.onmousemove = function(evt) {
        if (!mousePointer.drag) {
            return;
        }
        // dynamically update the content of the temporary layer
        tempContext.clearRect(0, 0, canvas.width, canvas.height);
        createRectangle(evt);
        drawRectangle(tempContext, rectangle);
    };

    wrapper.onclick = function(evt) {
        if (isPosOnRectangle()) {
            if (confirm('Please confirm bounding box position.')) {
                // move rectangle from temporary layer to main layer
                tempContext.clearRect(0, 0, canvas.width, canvas.height);
                drawRectangle(context, rectangle);
                rectangles.push(rectangle);

                socket.emit(
                    "bounding_box",
                    { type: "add", room: self_room, coordinates: rectangle }
                );
            } else {
                tempContext.clearRect(0, 0, canvas.width, canvas.height);
            }
            // reset rectangle attributes
            rectangle = {
                left: null,
                top: null,
                right: null,
                bottom: null
            };
        } else {
            if (confirm('Please confirm wish to remove bounding boxes.')) {
                context.clearRect(0, 0, canvas.width, canvas.height);
                rectangles = [];

                socket.emit(
                    "bounding_box",
                    { type: "remove", room: self_room }
                );
            }
        }
    };

    socket.on("bounding_box", (data) => {
        if (data.type === "add") {
            let rect = data.coordinates;
            if (data.user.id !== self_user.id) {
                drawRectangle(context, rect);
                rectangles.push(rect);
            }
        } else {
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    });
});
