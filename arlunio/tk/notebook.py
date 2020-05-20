import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import nbformat


class NbCell:
    """Mixin for common code across both cell types."""

    def resize_cell(self, cell):
        """Calculate the height a cell should be based on its contents"""

        end = cell.index("end-1c")
        lines = int(end.split(".")[0])

        cell.config(height=lines)


class MarkdownCell(tk.Frame, NbCell):
    """Our representation of a code cell."""

    def __init__(self, cell, parent=None):
        super().__init__(parent)
        self.pack(padx=10, pady=10)

        source = tk.Text(self)
        source.insert("1.0", cell.source)
        source["wrap"] = "word"
        self.resize_cell(source)

        source.pack()


class CodeCell(tk.Frame, NbCell):
    """Our representation of a code cell."""

    def __init__(self, cell, parent=None):
        super().__init__(parent)
        self.pack(padx=10, pady=10)

        source = tk.Text(self)
        source.insert("1.0", cell.source)
        self.resize_cell(source)
        source.pack(fill=tk.X, expand=True)


class NotebookViewer(tk.Frame):
    """A viewer for notebook files."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.init_menu()
        self.init_shortcuts()

    def init_menu(self):

        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.on_open)
        filemenu.add_command(label="Exit", command=self.on_quit, accelerator="Ctrl-Q")

        menubar.add_cascade(label="File", menu=filemenu)
        self.master.title("Notebook Editor | Arlunio")
        self.master.config(menu=menubar)

    def init_shortcuts(self):
        self.bind_all("<Control-o>", self.on_open)
        self.bind_all("<Control-q>", self.on_quit)

    def on_open(self, event=None):
        nb = filedialog.askopenfile(parent=self, filetypes=[("Notebook", "*.ipynb")])

        if nb is None:
            return

        notebook = nbformat.read(nb, as_version=nbformat.NO_CONVERT)

        for cell in notebook.cells:

            if cell.cell_type == "markdown":
                tkcell = MarkdownCell(cell, parent=self)

            if cell.cell_type == "code":
                tkcell = CodeCell(cell, parent=self)

        self.pack()

    def on_quit(self, event=None):
        self.quit()
