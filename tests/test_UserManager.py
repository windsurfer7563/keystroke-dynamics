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
