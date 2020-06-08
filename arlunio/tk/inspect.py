import inspect
import logging
import tkinter as tk
import tkinter.ttk as ttk

import arlunio.cli.debug as debug

from arlunio import Defn


class Inspector(ttk.Frame):
    """The arlunio inspector."""

    def __init__(self, module, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.logger = logging.getLogger(__name__)

        self.init_ui()
        self.load_module(module)

    def init_ui(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.input = tk.Text(self)
        self.input.config(height=15)
        self.input.grid(row=1, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self.source = tk.Text(self)
        self.source.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self.objects = ttk.Treeview(self)
        self.objects.grid(row=0, column=1, sticky=tk.N + tk.S + tk.E + tk.W)

        self.objects.column("#0", width=200)
        self.objects.heading("#0", text="Name")

        self.objects.bind("<Button-1>", self.on_select_object)

    def load_module(self, module):
        self.module = module

        defns = [
            v
            for v in module.__dict__.values()
            if inspect.isclass(v) and issubclass(v, Defn)
        ]

        for defn in sorted(defns, key=lambda o: o.__name__):
            self.objects.insert("", "end", text=defn.__name__)

    def on_select_object(self, event):

        id_ = self.objects.identify("item", event.x, event.y)
        name = self.objects.item(id_, "text")

        defn = getattr(self.module, name)
        code = inspect.getsource(defn)

        self.source.insert("end", code)
