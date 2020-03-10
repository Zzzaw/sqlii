import xml.etree.ElementTree

def loadXml(fname):
    data_list = []
    fo = open(fname)
    tmp = fo.read()
    root = xml.etree.ElementTree.fromstring(tmp)

    for test in root:
        data = load_child(test)
        data_list.append(data)
    return data_list

def load_child(parent):
    data = {}
    for child in parent:
        data[child.tag] = child.text
        if child.getchildren():
            data[child.tag] = load_child(child)
    return data

def loadErrorsXml(fname):
    fo = open(fname)
    tmp = fo.read()
    root = xml.etree.ElementTree.fromstring(tmp)

    errors = {}
    for dbms in root:
        errors[dbms.attrib['value']] = []
        for error in dbms:
            errors[dbms.attrib['value']].append(error.attrib['regexp'])

    return errors

if __name__ == '__main__':
    s = loadErrorsXml('../../data/xml/errors.xml')
    print(s)