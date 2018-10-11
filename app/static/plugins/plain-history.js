switch (element["type"]) {
    case "text":
        display_message(element["user"], element["timestamp"], element["msg"], element["receiver_id"] !== null);
        break;
    case "command":
        display_message(self_user, element["timestamp"], element["command"], true);
        break;
    case "status":
        break;
    case "new_image":
        set_image(latest_image)
}
