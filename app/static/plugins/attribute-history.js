switch (element.event) {
    case 'set_attribute':
        attribute_update(element);
        break;
    case 'set_text':
        text_update(element);
        break;
    case 'class_add':
        class_add(element);
        break;
    case 'class_removed':
        class_remove(element);
        break;
}
