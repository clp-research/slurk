switch (element.event) {
    case 'set_attribute':
        attribute_update(element.data);
        break;
    case 'set_text':
        text_update(element.data);
        break;
    case 'class_add':
        class_add(element.data);
        break;
    case 'class_removed':
        class_remove(element.data);
        break;
    case 'remove_attribute':
        remove_attribute;
        break;
}
