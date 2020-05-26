import logging
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk

import nbformat
import nbformat.v4 as nbv4

from arlunio.lib.image import decode
from jupyter_client import KernelManager
from PIL import ImageTk

from .components import View

logger = logging.getLogger(__name__)


def create_bind_tag(obj, tag, after=None, before=None):
    """Given a 'bindable' tk object, create a new "bind tag" and insert it into the
    event handler sequence.

    Parameters
    ----------
    obj:
        The Tk object to create the tag for
    tag:
        The name of the tag to create
    after:
        If given the created tag will be inserted after the given tag name.
    before:
        If given the created tag will be inserted before the given tag name.
    """

    if after is None and before is None:
        raise ValueError("Missing kw argument: 'before' or 'after'")

    if after is not None and before is not None:
        raise ValueError("Only one of 'before' OR 'after' can be set")

    tags = list(obj.bindtags())

    # To work as intended, tag names must be unique
    tag = str(obj).replace("!", "").replace(".", "") + "-" + tag

    name = after if after is not None else before
    offset = 1 if after is not None else 0

    index = tags.index(name) + offset
    tags.insert(index, tag)

    obj.bindtags(tuple(tags))

    logger.debug("Updated bind tags")
    logger.debug("%s: %s", str(obj), obj.bindtags())

    return tag


class NbCell(ttk.Frame):
    """Base class for common code across both cell types."""

    def __init__(self, cell, parent=None):
        super().__init__(parent)
        self.cell = cell

        self.textbox = tk.Text(self)
        self.textbox.insert("1.0", self.cell.source)

        self.textbox.bind("<Shift-Return>", self.on_run)

        # We want to only process the textbox after it's been updated to the latest
        # content.
        post_Text_hook = create_bind_tag(self.textbox, "post-Test", after="Text")
        self.textbox.bind_class(post_Text_hook, "<KeyPress>", self.on_input)

        # Ensure that the textbox has an appropriate size for the initial content.
        self.resize_textbox()
        self.textbox.grid(row=0, column=1, sticky=tk.N + tk.W + tk.E)

    def on_run(self, event):
        """Called whenever the user runs the cell."""

        logger.debug("Running cell: %s", self)

        # Suppress the default handler,
        return "break"

    def on_input(self, event):
        """Called whenever the user enters text."""
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

        # Placeholders to display cell outputs
        self.stream = None
        self.textdata = None
        self.imgdata = None

        # Populate the cell with any exising data
        self.exec_count = ttk.Label(
            self, text=self._fmt_exec_count(cell.execution_count), font="TkFixedFont"
        )
        self.exec_count.grid(row=0, column=0, sticky=tk.N + tk.W)
        self.add_output(cell.outputs)

    def _add_stream(self, output):
        """Add more text to the output stream"""

        if self.stream is None:
            self.stream = tk.Text(self)
            self.stream.grid(row=1, column=1)

            self.stream.tag_config("stderr", background="#d33", foreground="#333")
            self.stream.tag_config("stdout", foreground="#333")

        # The text widget needs to be enabled to modify text
        self.stream.config(state=tk.NORMAL)
        self.stream.insert("end", output.text, output.name)
        self.stream.config(state=tk.DISABLED)

        # Resize the box according to output size
        lines = int(self.stream.index("end-1c").split(".")[0])

        if self.stream.get("end-1c") == "\n":
            lines -= 1

        height = min(lines, 5)  # Max height of 5 lines.
        self.stream.config(height=height)
        self.stream.see("end-2c")

    def _fmt_exec_count(self, exec_count):

        if exec_count is None:
            return "[ ]: "

        return f"[{exec_count}]: "

    def _add_plain_text(self, txt):

        if txt is None:
            return

        prefix = "\n"

        if self.textdata is None:
            self.textdata = ttk.Label(self, text="", anchor=tk.W)
            self.textdata.grid(row=2, column=1, sticky=tk.W)
            prefix = ""

        self.textdata["text"] += prefix + txt

    def _add_image(self, image):

        if image is None:
            return

        if self.imgdata is not None:
            self.imgdata.destroy()

        image = decode(image)
        imagetk = ImageTk.PhotoImage(image)

        self.imgdata = ttk.Label(self, image=imagetk)
        self.imgdata.image = imagetk
        self.imgdata.grid(row=3, column=1)

    def add_output(self, outputs):
        """Process outputs for a cell."""

        for output in outputs:

            if output.output_type == "stream":
                self._add_stream(output)
                continue

            if output.output_type == "execute_result":
                data = output["data"]
                self._add_plain_text(data.get("text/plain", None))
                self._add_image(data.get("image/png", None))

                continue

    def on_run(self, event):
        code = self.textbox.get("1.0", "end-1c")
        msg = self.master.kclient.execute(code, timeout=60)

        logger.debug("Execute: %s", msg)
        idle = False

        while not idle:

            reply = self.master.kclient.get_iopub_msg()
            logger.debug(reply)

            if reply["msg_type"] == "status":
                idle = reply["content"]["execution_state"] == "idle"

        return "break"


class NotebookViewer(View):
    """A viewer for notebook files."""

    def __init__(self, parent=None):
        super().__init__(parent)

        #        self.init_menu()
        self.init_shortcuts()

        self.cells = []

        self.kmanager = KernelManager(kernel_name="python3")
        self.kmanager.start_kernel()

        self.kclient = self.kmanager.client()
        self.kclient.start_channels()

        try:
            self.kclient.wait_for_ready(timeout=60)
            logger.info("Kernel ready")
        except RuntimeError as exc:
            self.kclient.stop_channels()
            self.kmanager.shutdown_kernel()
            logger.error("Unable to start kernel", exc)

        nb = nbv4.new_notebook(cells=[nbv4.new_code_cell()])
        self.load_notebook(nb)

    def init_menu(self):

        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.on_open, accelerator="Ctrl-O")
        filemenu.add_command(label="Exit", command=self.on_quit, accelerator="Ctrl-Q")

        menubar.add_cascade(label="File", menu=filemenu)
        self.master.title("Notebook Editor | Arlunio")
        self.master.config(menu=menubar)

    def init_shortcuts(self):
        self.bind_all("<Control-o>", self.on_open)
        self.bind_all("<Control-q>", self.on_quit)

    def on_open(self, event=None):
        """Open a notebook with a file dialog."""

        nb = filedialog.askopenfile(parent=self, filetypes=[("Notebook", "*.ipynb")])

        if nb is None:
            return

        notebook = nbformat.read(nb, as_version=nbformat.NO_CONVERT)
        self.load_notebook(notebook)

    def load_notebook(self, notebook):
        """Load the given notebook object."""

        self.grid_columnconfigure(0, pad=10)
        self.grid_columnconfigure(1, pad=10)

        for cell in self.cells:
            cell.grid_remove()
            cell.destroy()

        for i, cell in enumerate(notebook.cells):
            self.grid_rowconfigure(i, pad=10)

            if cell.cell_type == "markdown":
                tkcell = MarkdownCell(cell, parent=self.view)

            if cell.cell_type == "code":
                tkcell = CodeCell(cell, parent=self.view)

            tkcell.grid(row=i, column=1)
            self.cells.append(tkcell)

        self.restart_kernel()

    def restart_kernel(self):
        pass

    def on_quit(self, event=None):

        self.kclient.stop_channels()
        self.kmanager.shutdown_kernel()

        self.quit()
