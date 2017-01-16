import os
from tkinter import *
from tkinter import ttk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showinfo
from passmanager import PasswordCollectionManager
from anomalydetector import AnomalyDetector

masterpasswd = '.tie5Roanl'

class KE_GUI:
    def __init__(self, master, passwd):
        self.master = master
        master.title("Keytroke evaluate")
        self.passwd = passwd
        self.currentUser = ""
        self.pc = PasswordCollectionManager(self.passwd,self)

        self.mainframe = ttk.Frame(master, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)

        self.userName_v = StringVar()
        ttk.Label(self.mainframe,text = 'Користувач:').grid(column=1, row=1, sticky=E)

        self.username_entry = ttk.Entry(self.mainframe, width=7, textvariable=self.userName_v, state='enabled')
        self.username_entry.grid(column=2, row=1, sticky=(W, E))
        self.username_entry.bind("<FocusOut>", self.username_entered)

        ttk.Label(self.mainframe, text='Пароль: ' + passwd).grid(column=2, row=2, sticky=(W,E))

        self.passwd_v = StringVar()
        self.pass_entry = ttk.Entry(self.mainframe, width=7, textvariable=self.passwd_v, state='enabled')
        self.pass_entry.grid(column=2, row=3, sticky=(W, E))

        self.pass_entry.bind("<FocusIn>", self.pass_collect)


        self.status_v = StringVar()
        ttk.Label(self.mainframe, textvariable=self.status_v).grid(column=3, row=6, sticky=(W,E))

        for child in self.mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

    def username_entered(self,evt):
        currentUser=self.userName_v.get()
        self.pc.change_user(currentUser)

    def pass_collect(self,evt):
        self.pc.password_evaluate()



root = Tk()
my_gui = KE_GUI(root, masterpasswd)
root.mainloop()
