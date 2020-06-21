from tkinter import *
from tkinter import ttk
from tkinter import filedialog

class AppGui():
    def __init__(self):
        self.gui = Tk()
        self.gui.geometry("400x400")
        self.gui.title("DXF Engraver")

        self.folderPath = StringVar()

    def getFolderPath(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)

    def doStuff(self):
        folder = self.folderPath.get()
        print("Doing stuff with folder", folder)

    def setup_gui(self):
        label = Label(self.gui, text="Enter name")
        label.grid(row=0, column = 0)

        folder_chooser = Entry(self.gui, textvariable=self.folderPath)
        folder_chooser.grid(row=0, column=1)

        find_button = ttk.Button(self.gui, text="Browse Folder", command=self.getFolderPath)
        find_button.grid(row=0,column=2)

        run_button = ttk.Button(self.gui, text="Do it!", command=self.doStuff)
        run_button.grid(row=0, column=3)

    def run(self):
        self.setup_gui()
        self.gui.mainloop()
