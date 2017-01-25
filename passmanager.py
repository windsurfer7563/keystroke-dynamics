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
            key1 = passwd[i]
            key2 = passwd[i+1] if i != pass_len - 1 else 'Return'


            if key2.isupper():
                columns.append('H.' + key1)
                columns.append('DD.' + key1 + '.SHIFT')
                columns.append('UD.' + key1 + '.SHIFT')
                key1 = 'SHIFT'

            if key1 == '.':
                key1 = 'PERIOD'
            if key2 == '.':
                key2 = 'PERIOD'



            columns.append('H.' + key1)
            columns.append('DD.' + key1 + '.' + key2)
            columns.append('UD.' + key1 + '.' + key2)

        return columns


    def eventlist_transform(self,eventList):
        #print(eventList)
        columns = self.getColumns(self.passwd)
        #print(columns)
        key_transform = lambda x: x if x =='Return' else str.upper(x)
        row=[]
        #створюємо список всіх часів для того щоб "якщо час більша за три стд відхилення - усереднюємо час"
        times = []

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
                times.append(time1)
            if action == 'UD':
                time1 =  eventList[key2]['D']-eventList[key1]['U']
                times.append(time1)
            #row[col]=time1
            row.append(time1)

        median = np.median(times)

        #усереднюєм значення в викидах
        for i in range(0,len(row),3):
            if row[i+1] > 0 and self.is_outlier(row[i+1], times, 3.) : row[i+1] = median
            if row[i+2] > 0 and self.is_outlier(row[i+2], times, 3.) : row[i+2] = median

        return row

    def is_outlier(self, x, data, m = 3.):
        d = np.abs(data - np.median(data))
        mdev = np.median(d)
        return 1 if np.abs(x - np.median(data))/mdev > m else 0



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
            try:
                ad=pickle.load(open(userFilePath,"rb"))
            except:
                self.wnd.status_v.set("Детектор не знайдено")
                return

            predict, dist, tresh = ad.predict(data)
            if not predict:
                self.wnd.status_v.set("Доступ дозволено")
            else:
                self.wnd.status_v.set("Доступ заборонено")

            self.wnd.status_dist.set("Dist: {0:.3f}".format(dist))
            self.wnd.status_tresh.set("Treshold: {0:.3f}".format(tresh))
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
        if event.Key != 'Return':
            self.storeEvent(event.Key,"U", event)
        return True


    def mainLoop(self):
        #    while not self.enterPressed:
        pythoncom.PumpWaitingMessages()

    def storeEvent(self, key, activity, event):
        global hookManager

        keystrokeTime = int(event.Time)
        if key == 'Oem_Period':
            key = 'PERIOD'

        if key == 'Lshift' or key == 'Rshift':
            key = 'SHIFT'

        if key in self.eventList:
            self.eventList[key].update({activity: int(keystrokeTime)})
        else:
            self.eventList[key] = {activity: int(keystrokeTime)}

        if key == 'Return':
            #print('Enter pressed')
            #self.enterPressed = True
            #hookManager.UnhookKeyboard()
            events = self.eventList
            self.eventList={}
            self.cb_function(events)
