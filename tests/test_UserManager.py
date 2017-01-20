from keystroke_learn import UserManager
from keystroke_learn import masterpasswd
from passmanager import PasswordCollectionManager
import os
import csv


def test_um_get_users():
    um = UserManager(masterpasswd)
    users = um.get_users()
    assert len(users) > 0


def test_um_file_write():
    um = UserManager(masterpasswd)
    um.getUserFileWriteSession('testuser')

    fileName = (os.path.join("accounts", 'testuser.csv'))
    f = open(fileName)
    reader=csv.reader(f, delimiter=',')
    assert next(reader) == PasswordCollectionManager.getColumns(None, passwd = masterpasswd)
    f.close()
    os.remove(fileName)



 #with f = open("/etc/passwd"):

#os.path.join("accounts", userFileName)

'''
{'Return': {'U': 263081599, 'D': 263081474}, '5': {'U': 263078494, 'D': 26307838
5}, 'E': {'U': 263077106, 'D': 263076981}, 'R': {'U': 263079072, 'D': 263078978}
, 'A': {'U': 263080273, 'D': 263080132}, 'L': {'U': 263080678, 'D': 263080554},
'PERIOD': {'U': 263076264, 'D': 263076154}, 'T': {'U': 263076591, 'D': 263076482
}, 'O': {'U': 263079976, 'D': 263079867}, 'N': {'U': 263080351, 'D': 263080257},
 'I': {'U': 263076810, 'D': 263076685}, 'Lshift': {'U': 263079087, 'D': 26307869
7}}
'''
