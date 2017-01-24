import pyHook
import pythoncom
import os
import csv
import pandas as pd
import numpy as np
import pickle



class PasswordCollectionManager(object):
    def __init__(self, passwd, wnd):
        self.passwd = passwd
        self.wnd = wnd
        pass

    def change_user(self,current_user):
        self.user = current_user


    def getColumns(self,passwd):
        columns = []
        key = ""
        key2 = ""
        pass_len=len(passwd)

        for i in range(pass_len):
            key = 'PERIOD' if passwd[i] == '.' else passwd[i]
            key2 = passwd[i+1] if i != pass_len - 1 else 'Return'
            columns.append('H.' + key)
            columns.append('DD.' + key + '.' + key2)
            columns.append('UD.' + key + '.' + key2)
        return columns

    def eventlist_transform(self,eventList):
        columns=self.getColumns(self.passwd)
        key_transform = lambda x: x if x =='Return' else str.upper(x)
        row=[]
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

            #row[col]=time1
            row.append(time1)
        return row

    def userRecordData(self, eventList):

        if self.wnd.passwd_v.get() != self.passwd:
            self.wnd.status_v.set("Пароль введено з помилкою!")
            self.wnd.pass_entry.state(['disabled'])
            self.wnd.passwd_v.set('')
            self.wnd.start_button.focus()
        else:
            #print(eventList)
            userFilePath = (os.path.join("accounts", self.user + '.csv'))
            #Read File to Grab Sessions
            df = pd.read_csv(userFilePath,header=0)

            row=self.eventlist_transform(eventList)
            df2=pd.DataFrame([row], columns=self.getColumns(self.passwd))
            df = df.append(df2, ignore_index=True)
            df.to_csv(userFilePath, index=False)

            self.wnd.status_v.set("OK")
            self.wnd.passwd_v.set('')
            self.wnd.start_button.focus()
            self.wnd.pass_entry.state(['disabled'])


    def userPassEvaluate(self, eventList):
        if self.wnd.passwd_v.get() != self.passwd:
            print(self.wnd.passwd_v.get())
            self.wnd.status_v.set("Невірний пароль!")
            self.wnd.passwd_v.set('')
            #self.wnd.username_entry.focus()
            #self.wnd.pass_entry.focus()
            #self.password_evaluate()
            #self.wnd.username_entry.focus()
        else:
            #print(eventList)
            self.wnd.passwd_v.set('')
            row=self.eventlist_transform(eventList)
            data = np.array(row, dtype=np.float)
            userFilePath =  (os.path.join("accounts", self.user + '_' + 'NN'+'.dat'))
            ad=pickle.load(open(userFilePath,"rb"))
            predict = ad.predict(data)
            self.wnd.status_v.set(predict)
            self.wnd.passwd_v.set('')
            #self.password_evaluate()
            #self.wnd.pass_entry.focus()
            #self.wnd.username_entry.focus()

    def password_collect(self):
        global hookManager

        if self.user == '': return

        keyLogger = KeyLogger(self.userRecordData)
        hookManager = pyHook.HookManager()
        hookManager.KeyDown = keyLogger.keyDownEvent
        hookManager.KeyUp = keyLogger.keyUpEvent
        hookManager.HookKeyboard()

    def password_evaluate(self):
        global hookManager

        if self.user == '': return

        keyLogger = KeyLogger(self.userPassEvaluate)
        hookManager = pyHook.HookManager()
        hookManager.KeyDown = keyLogger.keyDownEvent
        hookManager.KeyUp = keyLogger.keyUpEvent
        hookManager.HookKeyboard()


class KeyLogger(object):
    def __init__(self, funct):
        self.enterPressed = False
        self.eventList = {}
        self.passwd = ''
        self.cb_function=funct

    def keyDownEvent(self, event):
        self.storeEvent(event.Key,"D", event)
        return True

    def keyUpEvent(self, event):
        self.storeEvent(event.Key,"U", event)
        return True


    def mainLoop(self):
        pythoncom.PumpWaitingMessages()
            #while not self.enterPressed:
            #    pythoncom.PumpWaitingMessages()

    def storeEvent(self, key, activity, event):
        global hookManager

        keystrokeTime = int(event.Time)
        if key == 'Oem_Period':
            key = 'PERIOD'

        if key in self.eventList:
            self.eventList[key].update({activity: int(keystrokeTime)})
        else:
            self.eventList[key] = {activity: int(keystrokeTime)}

        # Chosen to use Escape key (ESC) due to input using a similar method
        # Enter Key - KeyCode: 13 Ascii: 13 ScanCode: 28 - ESC = 27 @ Ascii
        if event.Ascii == 13 and activity == "D":
            self.enterPressed = True
            #hookManager.UnhookKeyboard()
            events = self.eventList
            self.eventList={}
            self.cb_function(events)
