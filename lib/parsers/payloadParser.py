import re
import random
from lib.data.settings import *

def renderValue(orig, paramName, origValue, origValue_negative, replacements={}):
    new = orig
    used = {}
    for value in re.findall(r"\[_[A-Z_]+\]", orig):
        if value in replacements:
            new = new.replace(value, replacements[value])
        elif value == '[_PARAMNAME]':
            new = new.replace(value, paramName)
        elif value == '[_ORIGINAL]':
            new = new.replace(value, origValue)
        elif value == '[_ORIGINAL_NEGATIVE]':
            new = new.replace(value, origValue_negative)


    for value in re.findall(r"\[_RANDNUM\d+\]", orig):
        num = re.findall(r'\d+', value)[0]
        if num in used:
            rand = used[num]
            new = new.replace(value, str(used[num]))

        else:
            rand = random.randint(1,1000)
            while rand in used.values():
                rand = random.randint(1, 1000)
                used[num] = rand
        new = new.replace(value, str(rand))

    return new

def renderSQL(orig, replacements={}):
    new = orig
    for value in re.findall(r"\[[A-Z_]+\]", orig):
        if value in replacements:
            new = new.replace(value, replacements[value])
        elif value == '[QUOTE]':
            new = new.replace(value, '\'')
        elif value == '[COMMENT]':
            new = new.replace(value, '#')
        else:
            tmp = re.findall(r'[A-Z]+', value)[0]
            new = new.replace(value, tmp)

    for value in re.findall(r"\[[\+\-\*\/=\(\)]+\]", orig):
        if value in replacements:
            new = new.replace(value, replacements[value])
        else:
            tmp = re.findall(r'[\+\-\*\/=\(\)]+', value)[0]
            new = new.replace(value, tmp)

    return new



def renderPayloadTemplates(templates, test_param={}, valueReplace={}, sqlReplace={}):
    payloads = []
    for template in templates:
        payload = renderValue(template, valueReplace, test_param)
        payload = renderSQL(payload, sqlReplace)
        payloads.append(payload)

    return payloads

