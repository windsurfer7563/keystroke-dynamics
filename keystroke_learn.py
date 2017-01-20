import os
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
from os.path import basename
import csv

from passmanager import PasswordCollectionManager

from anomalydetector import AnomalyDetector

masterpasswd = '.tie5Roanl'

class UserManager(object):
    def __init__(self,passwd):
        self.users = []
        self.get_users()
        self.passwd=passwd

    #отримуємо список користувачів
    def get_users(self):
        self.users = []
        files = os.listdir(os.path.join("accounts"))
        files = filter(lambda x: x.endswith('.csv'),files)
        if files!=[]:
            for f in files:
                self.users.append(basename(f).split('.')[0])
        return self.users

    def getUserFileWriteSession(self, userName):
        if userName=='': return False

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
                headerwriter.writerow(PasswordCollectionManager.getColumns(None, passwd = self.passwd))
                writeFile.close()
                #showinfo("User Successfully Created", userFile)
            print("Your account has been created: ", userFile)

        return True

class KL_GUI:
    def __init__(self, master, passwd):
        self.master = master
        self.passwd = passwd
        self.currentUser = ""
        self.um = UserManager(self.passwd)
        self.pc = PasswordCollectionManager(self.passwd,self)

        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.userName_v = StringVar()
        ttk.Label(self.mainframe,text = 'Користувач:').grid(column=1, row=1, sticky=E)
        ttk.Label(self.mainframe,textvariable = self.userName_v).grid(column=2, row=1, sticky=W)
        ttk.Button(self.mainframe,text='Додати користувача',command = (lambda: self.add_user())).grid(column=3, row=1, sticky=E)

        self.listbox = Listbox(self.mainframe,selectmode=SINGLE, height=10)
        self.listbox.grid(column=2,row=3, sticky=(E,W))
        self.scrollbar = Scrollbar(self.mainframe, orient=VERTICAL)
        self.scrollbar.grid(column=2, row=3, sticky=(E,W,N,S))
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.change_listbox(self.um.get_users())

        self.listbox.bind('<<ListboxSelect>>', self.on_user_select)

        ttk.Label(self.mainframe, text='Введіть пароль: ' + passwd).grid(column=2, row=4, sticky=(W,E))

        self.start_button = ttk.Button(self.mainframe,text='Розпочати введення паролю',command = (lambda: self.pass_collect()))
        self.start_button.grid(column=2, row=5, sticky=(W, E))

        self.passwd_v = StringVar()
        self.pass_entry = ttk.Entry(self.mainframe, width=7, textvariable=self.passwd_v, state='disabled')
        self.pass_entry.grid(column=2, row=6, sticky=(W, E))

        self.status_v = StringVar()
        ttk.Label(self.mainframe, textvariable=self.status_v).grid(column=3, row=6, sticky=(W,E))

        self.fit_button = ttk.Button(self.mainframe,text='Навчання детектора',command = (lambda: self.fit_detector()))
        self.fit_button.grid(column=2, row=7, sticky=(W, E))

        self.status2_v = StringVar()
        ttk.Label(self.mainframe, textvariable=self.status2_v).grid(column=3, row=7, sticky=(W,E))


        ttk.Button(self.mainframe,text='Quit',command=(lambda: self.master.quit())).grid(column=3, row=8, sticky=E)


        for child in self.mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    def add_user(self):
        currentUser = askstring("Користувач","Задайте ім\'я користувача")
        if self.um.getUserFileWriteSession(currentUser):
            self.change_listbox(self.um.get_users())
            self.userName_v.set(self.currentUser)
            self.pc.change_user(self.currentUser)


    def on_user_select(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        selectedName = w.get(index)
        self.userName_v.set(selectedName)
        self.pc.change_user(selectedName)
        self.currentUser = selectedName

    def pass_collect(self):
        self.pass_entry.state(['!disabled'])
        self.pass_entry.focus()
        self.passwd_v.set('')
        self.status_v.set('')
        self.pc.password_collect()

    def fit_detector(self):
        self.mainframe.config(cursor="wait")
        self.mainframe.update()
        self.status2_v.set("")
        ad = AnomalyDetector(self.currentUser,'SVM')
        ad.fit()
        self.status2_v.set("OK")
        self.mainframe.config(cursor="")


    def change_listbox(self, users):
        self.listbox.delete(0, END)
        for user in users:
            self.listbox.insert(END,user)

if __name__ == '__main__':
    root = Tk()
    root.title("Keytroke capture")
    my_gui = KL_GUI(root, masterpasswd)
    root.mainloop()
