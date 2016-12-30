import os
import re
import json
import numpy
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
import pyHook
import pythoncom
import pandas as pd
import csv
from os.path import basename


passwd = '.tie5Roanl'

userName = ''
time_between_ups = []
time_between_downs = []

def getColumns(passwd):
    columns = []
    key = ""
    key2 = ""
    pass_len=len(passwd)
    for i in range(pass_len):
        if passwd[i] == '.':
            key = 'period'
        else:
            key = passwd[i]

        if i != pass_len - 1:
            key2 = passwd[i+1]
        else:
            key2 = 'Return'

        columns.append('H.' + key)
        columns.append('DD.' + key + '.' + key2)
        columns.append('UD.' + key + '.' + key2)

    return columns


'''
def getPathForFiles():
    current_path=os.path.abspath(os.curdir)
    iniFileName = os.path.join(current_path, 'keystrike.ini')
    textFile = open(iniFileName,'r')
    path = re.findall(r'path=(.*)', textFile.read())
    return path[0].strip()
'''

def get_users():
    files = os.listdir(os.path.join("accounts"))
    files = filter(lambda x: x.endswith('.csv'),files)
    user_res = []
    if files!=[]:
        for f in files:
            user_res.append(basename(f).split('.')[0])
    return (user_res)


def getUserFileWriteSession():
    global userName
    userName= askstring("Користувач","Задайте ім\'я користувача")
    global userName_v
    userName_v.set(userName)
    global passwd

    userFileName = (userName + ".csv")

    if os.path.exists(os.path.join("accounts", userFileName)):
        userFile = (os.path.join("accounts", userFileName))
    else:
        print("No File Exists! Creating New User")
        if os.path.exists(os.path.join("accounts", userFileName)):
            showinfo("Username exists! Load it or choose different name")
        else:
            userFile = (os.path.join("accounts", userFileName))
            writeFile = open(userFile, "w")
            headerwriter=csv.writer(writeFile, delimiter=',')
            headerwriter.writerow(getColumns(passwd))
            writeFile.close()
            #showinfo("User Successfully Created", userFile)
    print("Your account has been created: ", userFile)

    change_listbox(get_users())

def userRecordData(eventList):
    global userName
    global passwd
    userFilePath = (os.path.join("accounts", userName + '.csv'))
    #Read File to Grab Sessions
    df = pd.read_csv(userFilePath,header=0)

    columns=getColumns(passwd)

    key_transform = lambda x: x if x =='Return' else str.upper(x)
    row={}
    for col in columns:
        if col[0] == 'H':
            action, key1  = col.split('.')
            key1 = key_transform(key1)
        else:
            action, key1, key2 = col.split('.')
            key1 = key_transform(key1)
            key2 = key_transform(key2)


        if action == 'H':
            time1 = eventList[key1]['U']-eventList[key1]['D']
        if action == 'DD':
            time1 =  eventList[key2]['D']-eventList[key1]['D']
        if action == 'UD':
            time1 =  eventList[key2]['D']-eventList[key1]['U']

        row[col]=time1

    df = df.append(row, ignore_index=True)
    df.to_csv(userFilePath, index=False,)




def usernamePasswordInput():
    global pass_entry
    global status_v
    global hookManager
    global userName
    if userName =='': return


    keyLogger = KeyLogger()
    hookManager = pyHook.HookManager()
    hookManager.KeyDown = keyLogger.keyDownEvent
    hookManager.KeyUp = keyLogger.keyUpEvent
    hookManager.HookKeyboard()

    pass_entry.state(['!disabled'])
    pass_entry.focus()
    passwd_v.set('')
    status_v.set('')


class KeyLogger(object):
    def __init__(self):
        self.enterPressed = False
        self.eventList = {}
        self.passwd = ''

    def keyDownEvent(self, event):
        self.storeEvent(event.Key,"D", event)
        return True

    def keyUpEvent(self, event):
        self.storeEvent(event.Key,"U", event)
        return True


    def mainLoop(self):
            while not self.enterPressed:
                pythoncom.PumpWaitingMessages()

    def storeEvent(self, key, activity, event):
        global start_button
        global hookManager
        global status_v
        global passwd_v

        keystrokeTime = int(event.Time)
        if key == 'Oem_Period':
            key = 'PERIOD'

        if key in self.eventList:
            self.eventList[key].update({activity: int(keystrokeTime)})
        else:
            self.eventList[key] = {activity: int(keystrokeTime)}

        # Chosen to use Escape key (ESC) due to input using a similar method
        # Enter Key - KeyCode: 13 Ascii: 13 ScanCode: 28 - ESC = 27 @ Ascii
        if event.Ascii == 13:
            self.enterPressed = True
            if passwd_v.get() == passwd:
                status_v.set("OK")
                passwd_v.set('')
                hookManager.UnhookKeyboard()
                start_button.focus()
                pass_entry.state(['disabled'])
                userRecordData(self.eventList)
            else:
                print(passwd_v.get())
                status_v.set("Невірний пароль!")
                pass_entry.state(['disabled'])
                passwd_v.set('')
                hookManager.UnhookKeyboard()
                start_button.focus()




def change_listbox(users):
    global listbox
    listbox.delete(0, END)
    for  user in users:
        listbox.insert(END,user)

def change_user(selectedName):
    global userName
    global userName_v
    userName = selectedName
    userName_v.set(selectedName)


def onselect(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    selectedName = w.get(index)
    change_user(selectedName)





window = Tk()
window.title('Keytroke capture')

mainframe = ttk.Frame(window, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


userName_v = StringVar()
ttk.Label(mainframe,text = 'Користувач:').grid(column=1, row=1, sticky=E)

ttk.Label(mainframe,textvariable = userName_v).grid(column=2, row=1, sticky=W)

ttk.Button(mainframe,text='Додати користувача',command = (lambda: getUserFileWriteSession())).grid(column=3, row=1, sticky=E)


listbox = Listbox(mainframe,selectmode=SINGLE, height=10)
listbox.grid(column=2,row=3, sticky=(E,W))
scrollbar = Scrollbar(mainframe, orient=VERTICAL)
scrollbar.grid(column=2, row=3, sticky=(E,W,N,S))
scrollbar.config(command=listbox.yview)
listbox.config(yscrollcommand=scrollbar.set)

change_listbox(get_users())

listbox.bind('<<ListboxSelect>>', onselect)

ttk.Label(mainframe, text='Введіть пароль: ' + passwd).grid(column=2, row=4, sticky=(W,E))
start_button = ttk.Button(mainframe,text='Розпочати введення паролю',command = (lambda: usernamePasswordInput()))
start_button.grid(column=2, row=5, sticky=(W, E))



passwd_v = StringVar()
pass_entry = ttk.Entry(mainframe, width=7, textvariable=passwd_v, state='disabled')
pass_entry.grid(column=2, row=6, sticky=(W, E))


status_v = StringVar()
ttk.Label(mainframe, textvariable=status_v).grid(column=3, row=6, sticky=(W,E))


ttk.Button(mainframe,text='Quit',command=(lambda: window.quit())).grid(column=3, row=8, sticky=E)


for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)



window.mainloop()
