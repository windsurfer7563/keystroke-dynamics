from passmanager import PasswordCollectionManager
from keystroke_learn import KL_GUI
import os
import csv

from unittest import mock

def test_userRecordData():
    passwd = '.tie5Roanl'
    eventList = {'Return': {'U': 263081599, 'D': 263081474}, '5': {'U': 263078494, 'D': 263078385},
    'E': {'U': 263077106, 'D': 263076981}, 'R': {'U': 263079072, 'D': 263078978},
    'A': {'U': 263080273, 'D': 263080132}, 'L': {'U': 263080678, 'D': 263080554},
    'PERIOD': {'U': 263076264, 'D': 263076154}, 'T': {'U': 263076591, 'D': 263076482},
    'O': {'U': 263079976, 'D': 263079867}, 'N': {'U': 263080351, 'D': 263080257},
    'I': {'U': 263076810, 'D': 263076685}, 'Lshift': {'U': 263079087, 'D': 263078697}}

    #my_gui = KL_GUI(None, passwd)

    m = mock.Mock()
    pc = PasswordCollectionManager(passwd,m)
    pc.change_user('testuser2')
    pc.userRecordData(eventList)

    userFilePath = (os.path.join("accounts", 'testuser2.csv'))
    f = open(userFilePath)
    reader=csv.reader(f, delimiter=',')
    assert len(next(reader)) == 30
    f.close()
