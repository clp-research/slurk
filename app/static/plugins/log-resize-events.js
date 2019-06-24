function log_resize_event() {
    socket.emit('log', { room: self_room, type: "resize", width: $(window).width(), height: $(window).height() });
}

var resizeTimer;
$(window).resize(function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(log_resize_event, 500);
});

// Initial size of window. Otherwise it's hard to track changes
log_resize_event()
