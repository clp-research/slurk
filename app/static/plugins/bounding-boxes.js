var canvas, canvas_position, swap, img, imgWrapper, context, mouse, rectangle;

mouse = {
    click: false,
    move: false,
    pos: {x:null, y:null},
    drag_start: null
  };
rectangle = {
    p1: null,
    p2: null,
    width: null,
    height: null
  };

img = document.getElementById('current-image');
canvas  = document.getElementById('canvas');
if (canvas == null) {
  // if there's no canvas element: create canvas and fit it over the image
  canvas = document.createElement('canvas');
  canvas.id = "canvas";
  canvas.width = img.clientWidth;
  canvas.height = img.clientHeight;
  canvas.style.zIndex = 100;
  canvas.style.position = "absolute";
  canvas.style.top = "0px";
  canvas.style.left = "0px";
  $(img).wrap("<div id='img-wrapper' style='position:relative;'></div>");
  imgWrapper = document.getElementById("img-wrapper");
  imgWrapper.appendChild(canvas);
}

// create and configure context
context = canvas.getContext('2d');
context.fillStyle = "rgba(255,0,0,0.2)";
context.strokeStyle = 'red';
context.lineWidth = 2;

function getPosition (evt) {
    /*
    assign the cursor position within #canvas to mouse.pos
    */
    canvas_position = $('#canvas').offset();
    mouse.pos.x = evt.clientX - canvas_position.left;
    mouse.pos.y = evt.clientY - canvas_position.top;
}

function drawRectangle(){
  /*
  draw a rectangle based on the coordinates of mouse.p1
  and the current mouse position
  */
  rectangle.p2 = {x: mouse.pos.x, y: mouse.pos.y};
  rectangle.width = mouse.pos.x-rectangle.p1.x;
  rectangle.height = mouse.pos.y-rectangle.p1.y;
  context.clearRect(0,0,canvas.width,canvas.height); //clear canvas
  context.beginPath();
  context.fillRect(rectangle.p1.x, rectangle.p1.y, rectangle.width, rectangle.height);
  context.rect(rectangle.p1.x, rectangle.p1.y, rectangle.width, rectangle.height);
  context.stroke();
}

function normalizeRectangle(){
  /*
  make sure rectangle.p1 is the upper-left corner and the values of
  both rectangle.width and rectangle.height are positive
  */
  if (rectangle.p1.x > rectangle.p2.x) {
    swap = rectangle.p1.x;
    rectangle.p1.x = rectangle.p2.x;
    rectangle.p2.x = swap;
    rectangle.width = rectangle.p2.x - rectangle.p1.x;
  }
  if (rectangle.p1.y > rectangle.p2.y) {
    swap = rectangle.p1.y;
    rectangle.p1.y = rectangle.p2.y;
    rectangle.p2.y = swap;
    rectangle.height = rectangle.p2.y - rectangle.p1.y;
  }
}

function posOnRectangle(){
  /*
  return true if cursor position is within a drawn rectangle, otherwise return false
  */
  normalizeRectangle();
  if ((mouse.pos.x >= rectangle.p1.x && mouse.pos.x <= rectangle.p2.x && mouse.pos.y >= rectangle.p1.y && mouse.pos.y <= rectangle.p2.y)) {
    return true;
  } else {return false;}
}

img.onload = function (){
    // refresh canvas size and context properties
    canvas.width = img.clientWidth;
    canvas.height = img.clientHeight;
    context.fillStyle = "rgba(255,0,0,0.2)";
    context.strokeStyle = 'red';
    context.lineWidth = 2;
};

canvas.onmousedown = function(e){
    getPosition(e);
    mouse.drag_start = {x: mouse.pos.x, y: mouse.pos.y};
    mouse.click = true;
};

canvas.onmouseup = function(e){
    mouse.click = false;
};

canvas.onmousemove = function(e) {
    getPosition(e);
    if(mouse.click) {
        rectangle.p1 = mouse.drag_start;
        mouse.move = true;
        drawRectangle();
    }
};

canvas.onclick = function(e) {
  if (mouse.move == false) {
    // if user clicks without dragging
    getPosition(e)
    if (posOnRectangle()) {
      // if user clicks on drawn rectangle: confirm position and emit
      if (confirm('Please confirm bounding box position.')) {
        console.log("bounding box:", rectangle)
        socket.emit('mousePosition', {
            type:'bb',
            coordinates:{
              x: rectangle.p1.x,
              y: rectangle.p1.y,
              width: rectangle.width,
              height: rectangle.height
            },
            element:"#canvas",
            room:self_room
        });
      }
    } else {
      // if user clicks on empty space around rectangle: clear canvas
      context.clearRect(0, 0, canvas.width, canvas.height);
      rectangle = {p1: null, p2: null, width: null, height: null};
    }
  } else {
    // if mouse button is released after drawing
    mouse.move = false;
  }
};
