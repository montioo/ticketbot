# https://docs.python.org/2/library/xml.etree.elementtree.html

from xml.etree import ElementTree
import utility as util

filename = 'users.xml'


def get_users(user_type):
    tree = ElementTree.parse(filename)
    root = tree.getroot()

    xml_id_elements = root.find(user_type).findall('chat_id')

    id_list = []

    for e in xml_id_elements:
        id_list.append(e.text)

    return id_list


def remove_user(user_type, chat_id):

    if not user_exists(user_type, chat_id):
        return

    output = util.get_time_string() + ": xmlDb, remove " + chat_id + " from " + user_type
    print(output)

    tree = ElementTree.parse(filename)
    root = tree.getroot()

    users = root.find(user_type)

    for e in users.findall('chat_id'):
        if e.text == chat_id:
            users.remove(e)

    tree.write(filename)


def add_user(user_type, chat_id):

    if user_exists(user_type, chat_id):
        return

    output = util.get_time_string() + ": xmlDb, add " + chat_id + " to " + user_type
    print(output)

    tree = ElementTree.parse(filename)
    root = tree.getroot()

    users = root.find(user_type)

    new_elem = ElementTree.Element("chat_id")
    new_elem.text = chat_id
    users.append(new_elem)

    tree.write(filename)


def user_exists(user_type, chat_id):
    users = get_users(user_type)

    return chat_id in users


def main():
    # Tests
    print(get_users('users'))
    add_user('users', '2727018')
    add_user('users', '2727018')
    print(get_users('users'))
    remove_user('users', '2727018')
    print(get_users('users'))


if __name__ == "__main__":
    main()
