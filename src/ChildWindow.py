import tkinter as tk
from tkinter import ttk

import GUIDataStructs as gds

class ChildWindow(tk.Toplevel):
    def __init__(self, root, name="1d Plot"):
        self.root = root
        tk.Toplevel.__init__(self, self.root)
        self.title(name)
        self.protocol("WM_DELETE_WINDOW", self.onClose)

        self.withdraw()

    def onClose(self):
        self.withdraw()

    def Show(self):
        self.deiconify()
