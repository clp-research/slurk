//Note: initiating fullscreen with F11 does not remove the overlay
document.addEventListener("fullscreenchange", fullScreenChange);
document.addEventListener("mozfullscreenchange", fullScreenChange); // firefox
document.addEventListener("webkitfullscreenchange", fullScreenChange); // safari, chrome, opera
document.addEventListener("msfullscreenchange", fullScreenChange); // IE

// enter fullscreen mode
function enterFullscreen(element) {
    if (element.requestFullscreen) {
        element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
	// safari, chrome, opera
        element.webkitRequestFullscreen();
    } else if (element.mozRequestFullScreen) {
	// firefox
        element.mozRequestFullScreen();
    } else if (element.msRequestFullscreen) {
	// IE
        element.msRequestFullscreen();
    }
}

// disable fullscreen mode
function closeFullscreen() {
    if (statusFullScreen()) {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
	    // safari, chrome, opera
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
	    // firefox
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
	    // IE
            document.msExitFullscreen();
        }
    }
}

// return true if browser is in fullscreen
function statusFullScreen() {
    if (
        document.fullscreenElement
	|| document.mozFullScreenElement
	|| document.webkitFullscreenElement
	|| document.msFullscreenElement
    ) {
        return true;
    } else {
        return false;
    }
}

// hide overlay when in fullscreen, show it otherwise
function fullScreenChange() {
    if (statusFullScreen()) {
        $("#fullscreen-overlay").fadeOut();
    } else {
        $("#fullscreen-overlay").fadeIn();
	$("#fullscreenButton").fadeIn();
    }
}


fullScreenChange();
$("#fullscreenButton").click(function(e) {
    enterFullscreen(document.documentElement);
});
