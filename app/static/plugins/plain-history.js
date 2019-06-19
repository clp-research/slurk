switch (element.event) {
    case 'text_message':
        display_message(
            element.user,
            element.date_modified,
            element.message,
            element.receiver !== null);
        break;
    case 'image_message':
        display_image(
            element.user,
            element.date_modified,
            element.url,
            element.width,
            element.height,
            element.receiver !== null);
        break;
}
