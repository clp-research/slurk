if (element.date_modified !== null)
    date = element.date_modified
else
    date = element.date_created

if (element.event === 'text_message') {
    if (element.data.html) {
        $.getScript('https://cdn.jsdelivr.net/npm/showdown@1.9.0/dist/showdown.min.js', () => {
            const converter = new showdown.Converter();
            display_message(
                element.user,
                date,
                converter.makeHtml(element.data.message),
                element.receiver !== null,
                true);
        });
    } else {
        display_message(
            element.user,
            date,
            element.data.message,
            element.receiver !== null);
    }
} else if (element.event === "image_message") {
    display_image(
        element.user,
        date,
        element.data.url,
        element.data.width,
        element.data.height,
        element.receiver !== null);
}
