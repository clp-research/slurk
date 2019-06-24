const BORDERSIZE = 7;

$(document).ready(() => {
    const sidebar = document.getElementById("sidebar");
    const content = document.getElementById("content");

    let splitter_pos;

    function resize(e) {
        const dx = splitter_pos - e.x;
        splitter_pos = e.x;
        sidebar.style.width = (parseInt(getComputedStyle(sidebar, '').width + BORDERSIZE) + dx) + "px";
        content.style.width = (parseInt(getComputedStyle(content, '').width + BORDERSIZE) - dx) + "px";
    }

    sidebar.addEventListener("mousedown", function (e) {
        // console.log("mousedown", e.offsetX);
        if (e.offsetX < BORDERSIZE) {
            splitter_pos = e.x;
            document.addEventListener("mousemove", resize, false);
        }
    }, false);

    document.addEventListener("mouseup", function () {
        document.removeEventListener("mousemove", resize, false);
    }, false);
});