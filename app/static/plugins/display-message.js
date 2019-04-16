if (data["url"] !== undefined) {
    display_image(data.user, data.timestamp, data.url, data.width, data.height, data.privateMessage);
} else {
    display_message(data.user, data.timestamp, data.msg, data.privateMessage);
}
