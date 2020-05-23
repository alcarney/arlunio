import logging
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import nbformat

logger = logging.getLogger(__name__)


class NbCell(tk.Frame):
    """Base class for common code across both cell types."""

    def __init__(self, cell, parent=None):
        super().__init__(parent)
        # self.pack(padx=10, pady=10)

        self.cell = cell

        self.textbox = tk.Text(self)
        self.textbox.insert("1.0", self.cell.source)

        # We want to resize the textbox only once the default Text handler
        # has processed the event. So using the concept of "bind tags" we can
        # create a custom tag in the event handler chain right where we need it
        # to be and then bind to that.
        #
        # https://stackoverflow.com/questions/2458026/python-gui-events-out-of-order
        # https://stackoverflow.com/questions/40421993/confused-about-tkinter-bind-class
        btags = list(self.textbox.bindtags())
        index = btags.index("Text")

        wid = str(self.textbox).replace("!", "").replace(".", "")
        tag = f"{wid}-post-Text"  # Tag must be unique
        btags.insert(index + 1, tag)

        self.textbox.bindtags(tuple(btags))
        self.textbox.bind_class(tag, "<KeyPress>", self.on_input)

        # Ensure that the textbox has an appropriate size for the initial content.
        self.resize_textbox()
        self.textbox.grid(row=0)

    def on_input(self, event):
        """Called whenever the user enters text."""
        logger.debug("%s", self.textbox)
        self.resize_textbox()

    def resize_textbox(self):
        """Calculate the height a cell should be based on its contents

        TODO: Handle the case where we have line wrapping enabled.
        """
        end = self.textbox.index("end-1c")

        lines = int(end.split(".")[0])
        self.textbox.config(height=lines)


class MarkdownCell(NbCell):
    """A NbCell specialised to handle markdown content."""

    def __init__(self, cell, parent=None):
        super().__init__(cell, parent)
        self.textbox["wrap"] = "word"


class CodeCell(NbCell):
    """An NbCell specialised to handle code."""

    def __init__(self, cell, parent=None):
        super().__init__(cell, parent)


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

        for i, cell in enumerate(notebook.cells):
            logger.debug("Loading cell: %s", i)

            if cell.cell_type == "markdown":
                tkcell = MarkdownCell(cell, parent=self)

            if cell.cell_type == "code":
                tkcell = CodeCell(cell, parent=self)

                label = ttk.Label(self, text="[ ]: ")
                label.grid(row=i, column=0)
                label.config(anchor=tk.N)

            tkcell.grid(row=i, column=1)

    def on_quit(self, event=None):
        self.quit()
