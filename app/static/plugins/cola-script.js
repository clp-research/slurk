// Remove the second header as we don't need it.
$('h2').remove();

// Create the necessary tags for the help button and its content
// and append them to the <nav>-tag.
$('nav').append('<button class="button">HELP' +
                  '<div class="button_content">' +
                  '<p><u>Commands to use in this game:</u></p><br>' +
                  '<p><b><font color="red">/answer <i>...one sentence description here...</font></i></b><br><br>' +
                    'For example, /answer "XYZ" has black body and white wings. <br>' +
                    'This command can be used multiple times until both the players reach an agreement.' +
                  '</p><br><br>' +
                  '<p><b><font color="red">/agree</font></b><br><br>' +
                    'This command can be used only once<br>' +
                    'for final submission by one of the players.<br>' +
                    'Use this command only when you reach an agreement.<br>' +
                  '</p>' +
                  '</div>' +
                '</button>');

// Zoom function: When you click on a picture
// this function gets called; the image with its
// original size will pop up.
function zoom(image) {
    var zoom_bg = document.getElementById('zoom');
    zoom_bg.style.display = "block";
    var url = image.getAttribute('src')
    var orig_image_size = `<img src=` + url + `>`;
    $('#original_img_size').empty();
	$('#original_img_size').append(orig_image_size);
    var width = document.getElementById("show-area").offsetWidth;
    var height = document.getElementById("show-area").offsetHeight;
    document.getElementById("zoom").style.width = width+'px';
    document.getElementById("zoom").style.height = height+'px';
}

// Zoom close: Click on the zoomed-in picture or on
// the transparent background to close the zoom.
function close_zoom() {
    var zoom_bg = document.getElementById('zoom');
    zoom_bg.style.display = "none";
}
