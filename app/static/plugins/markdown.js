if (data.html) {
    $.getScript('https://cdn.jsdelivr.net/npm/showdown@1.9.0/dist/showdown.min.js', () => {
        const converter = new showdown.Converter();
        display_message(data.user, data.timestamp, converter.makeHtml(data.msg), data.private, true);
    });
} else {
    display_message(data.user, data.timestamp, data.msg, data.private, false);
}
