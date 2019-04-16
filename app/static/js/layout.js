$(document).ready(() => {
    socket.on('attribute_update', function (data) {
        // console.log("Attribute updated:", data);
        if (data.id)
            $('#' + data.id).attr(data.attribute, data.value).show();
        if (data.class)
            $('.' + data.class).attr(data.attribute, data.value).show();
        if (data.element)
            $(data.element).attr(data.attribute, data.value).show();
    });

    socket.on('class_add', function (data) {
        // console.log("Class added:", data);
        $('#' + data.id).addClass(data.class);
    });

    socket.on('class_remove', function (data) {
        // console.log("Class removed:", data);
        $('#' + data.id).removeClass(data.class);
    });

    socket.on('text_update', function (data) {
        // console.log("Text updated:", data);
        $('#' + data.id).text(data.text).show();
    });
});
