if (data["image"] !== undefined) {
    display_image(data.user, getTime(data.timestamp), data.image, data.width, data.height, data.privateMessage);
} else {
    display_message(data.user, data.timestamp, data.msg, data.privateMessage);
}