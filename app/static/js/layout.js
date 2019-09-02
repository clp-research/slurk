function attribute_update(data) {
    // console.log("Attribute updated:", data);
    if (data.id)
        $('#' + data.id).attr(data.attribute, data.value).show();
    if (data.class)
        $('.' + data.class).attr(data.attribute, data.value).show();
    if (data.element)
        $(data.element).attr(data.attribute, data.value).show();
}

function class_add(data) {
    // console.log("Class added:", data);
    $('#' + data.id).addClass(data.class);
}

function class_remove(data) {
    // console.log("Class removed:", data);
    $('#' + data.id).removeClass(data.class);
}

function text_update(data) {
    // console.log("Text updated:", data);
    $('#' + data.id).text(data.text).show();
}

$(document).ready(() => {
    socket.on('attribute_update', attribute_update);
    socket.on('class_add', class_add);
    socket.on('class_remove', class_remove);
    socket.on('text_update', text_update);
});
