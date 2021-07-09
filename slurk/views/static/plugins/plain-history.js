if (element.date_modified !== null)
    date = element.date_modified
else
    date = element.date_created

switch (element.event) {
    case 'text_message':
        display_message(
            element.user,
            date,
            element.data.message,
            element.receiver !== null);
        break;
    case 'image_message':
        display_image(
            element.user,
            element.date_modified,
            element.data.url,
            element.data.width,
            element.data.height,
            element.receiver !== null);
        break;
}
