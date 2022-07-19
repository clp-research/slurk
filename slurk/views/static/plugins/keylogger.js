$(document).ready(() => {
    $('#text').keyup(function (e){
        unwanted = ["Shift", "Control", "Alt", "AltGraph"]
        if (!unwanted.includes(e.key)){ 
            socket.emit(
                "keystroke",
                { "key": e.key,
                "alt": e.altKey,
                "ctrl": e.ctrlKey,
                "shift": e.shiftKey
                }
            );
        }
    })
});
