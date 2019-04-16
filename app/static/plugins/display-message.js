if (data["url"] !== undefined) {
    display_image(data.sender, data.timestamp, data.url, data.width, data.height, data.privateMessage);
} else {
    display_message(data.sender, data.timestamp, data.msg, data.privateMessage);
}
