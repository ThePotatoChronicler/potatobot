#!/usr/bin/python
from cryptography.fernet import Fernet
from sys import argv, stdout

with open('christmas_key.fernet', 'rb') as f:
    christmas = Fernet(f.read())

with open(argv[1], 'rb') as f:
    stdout.buffer.write(christmas.encrypt(f.read()))
