import random
import string

def randomInt():
    return random.randint(1,1000)

def randomStr(len):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))