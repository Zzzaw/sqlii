import time

localtime = time.strftime("%H:%M:%S", time.localtime())

def info(msg):
    msg = '[{}] [INFO] {}'.format(localtime, msg)
    print(msg)

def error(msg):
    msg = '[{}] [ERROR] {}'.format(localtime, msg)
    print(msg)

def warn(msg):
    msg = '[{}] [WARNING] {}'.format(localtime, msg)
    print(msg)

def puts(msg):
    print(msg)
