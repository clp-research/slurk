if (data["image"] !== undefined) {
    submit_image(data.user, getTime(data.timestamp), data.image, data.width, data.height, data.privateMessage);
} else {
    submit_message(data.user, data.timestamp, data.msg, data.privateMessage);
}