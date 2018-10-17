# https://docs.python.org/2/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET

filename = 'users.xml'

def getUsers (user_type):
    tree = ET.parse(filename)
    root = tree.getroot()

    xml_id_elements = root.find(user_type).findall('chat_id')

    id_list = []

    for e in xml_id_elements:
        id_list.append(e.text)

    return id_list


def removeUser (user_type, chat_id):

    tree = ET.parse(filename)
    root = tree.getroot()

    users = root.find(user_type)

    for e in users.findall('chat_id'):
        if e.text == chat_id:
            users.remove(e)

    tree.write(filename)


def addUser (user_type, chat_id):

    tree = ET.parse(filename)
    root = tree.getroot()

    users = root.find(user_type)

    new_elem = ET.Element("chat_id")
    new_elem.text = chat_id
    users.append(new_elem)

    tree.write(filename)


def main():
    # Tests
    print(getUsers('users'))
    addUser('users', '2727018')
    print(getUsers('users'))
    removeUser('users', '2727018')
    print(getUsers('users'))



if __name__ == "__main__":
    main()
