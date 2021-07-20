if (element.event === 'text_message') {
    if (element.data.html) {
        display_message(
            element.user,
            element.date_modified !== null ? element.date_modified : element.date_created,
            markdown.makeHtml(element.data.message),
            element.receiver !== null,
            true);
    } else {
        display_message(
            element.user,
            element.date_modified !== null ? element.date_modified : element.date_created,
            element.data.message,
            element.receiver !== null);
    }
} else if (element.event === "image_message") {
    display_image(
        element.user,
        element.date_modified !== null ? element.date_modified : element.date_created,
        element.data.url,
        element.data.width,
        element.data.height,
        element.receiver !== null);
}
