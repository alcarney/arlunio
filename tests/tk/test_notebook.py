import tkinter as tk

import nbformat.v4 as nb
import PIL.Image as Image
import py.test

from arlunio.lib.image import encode
from arlunio.tk.notebook import CodeCell, MarkdownCell


@py.test.fixture(scope="function")
def tk_root():
    """Fixture that handles setup/teardown of tk test cases."""

    root = tk.Tk()
    root.deiconify()

    yield root

    root.update()

    for w in root.winfo_children():
        w.destroy()

    root.destroy()


class TestCodeCell:
    """Test cases for the code cell ui component"""

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height",
        [
            (None, 1),
            ("print('Hello, World!')", 1),
            ("def f(a,b):\n    '''A docstring.'''\n    return a + b", 3),
        ],
    )
    def test_init_cell(self, tk_root, txt, height):
        """Ensure that the cell handles being given an empty code cell"""

        cell = nb.new_code_cell()

        if txt is not None:
            cell.source = txt

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=1)

        assert code_cell.textbox.cget("height") == height

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height,final",
        [
            ("abc", 1, "abc"),
            ("abc\ndef", 2, "abc\ndef"),
            ("abc\n\ndef", 3, "abc\n\ndef"),
            ("abc\ndef\nx\x08\x08", 2, "abc\ndef"),
        ],
    )
    def test_cell_resizes_on_input(self, tk_root, txt, height, final):
        """Ensure that the code cell resizes based on user input."""

        cell = nb.new_code_cell()

        code_cell = CodeCell(cell, parent=tk_root)
        code_cell.grid(row=1)
        tk_root.update()

        code_cell.textbox.focus_force()

        for c in txt:
            sym = c

            if sym == "\n":
                sym = "Return"

            if sym == "\x08":
                sym = "BackSpace"

            code_cell.textbox.event_generate("<KeyPress>", keysym=sym)

        value = code_cell.textbox.get("1.0", "end-1c")
        assert value == final

        assert code_cell.textbox.cget("height") == height

    @py.test.mark.tk
    def test_stream(self, tk_root):
        """Ensure that we can add output to a cell that didn't previously have any."""

        cell = CodeCell(nb.new_code_cell(), parent=tk_root)
        cell.grid(row=1)
        cell.add_stream_output("Hi there.")

        tk_root.update()
        assert cell.stream["text"] == "Hi there."

    @py.test.mark.tk
    def test_stream_multiple(self, tk_root):
        """Ensure that we can add output to a cell incrementally."""

        cell = CodeCell(nb.new_code_cell(), parent=tk_root)
        cell.grid(row=1)
        cell.add_stream_output("Hello\n")
        cell.add_stream_output("World\n")

        tk_root.update()
        assert cell.stream["text"] == "Hello\nWorld\n"

    @py.test.mark.tk
    def test_textdata(self, tk_root):
        """Ensure that we can associate text data to a cell that didn't previously have
        any."""

        data = {"text/plain": "3"}

        cell = CodeCell(nb.new_code_cell(), parent=tk_root)
        cell.grid(row=1)
        cell.add_data_output(data)

        tk_root.update()
        assert cell.textdata["text"] == "3"

    @py.test.mark.tk
    def test_textdata_multiple(self, tk_root):
        """Ensure that we can associate text data to a cell incrementally."""

        data = {"text/plain": "3"}
        data2 = {"text/plain": "4"}
        data3 = {"text/plain": "5"}

        cell = CodeCell(nb.new_code_cell(), parent=tk_root)
        cell.grid(row=1)
        cell.add_data_output(data)
        cell.add_data_output(data2)
        cell.add_data_output(data3)

        tk_root.update()
        assert cell.textdata["text"] == "3\n4\n5"

    @py.test.mark.tk
    def test_imgdata(self, tk_root, testdata):
        """Ensure that we can associate an image with a cell"""

        imgpath = testdata("tk/circle.png", path_only=True)
        img = Image.open(imgpath)
        image = encode(img).decode("utf-8")

        data = {"image/png": image + "\n"}

        cell = CodeCell(nb.new_code_cell(), parent=tk_root)
        cell.grid(row=1)
        cell.add_data_output(data)

        tk_root.update()
        assert cell.imgdata is not None  # Is there a better check than this?


class TestMarkdownCell:
    """Test cases for the markdown cell ui component"""

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height",
        [(None, 1), ("# Hello World", 1), ("- Item one\n- Item two\n-Item three", 3)],
    )
    def test_init(self, tk_root, txt, height):
        """Ensure that a cell can be created successfully based on an existing cell."""

        cell = nb.new_markdown_cell()

        if txt is not None:
            cell.source = txt

        md_cell = MarkdownCell(cell, parent=tk_root)
        md_cell.grid(row=1)

        assert md_cell.textbox.cget("height") == height
        assert md_cell.textbox.cget("wrap") == "word"

    @py.test.mark.tk
    @py.test.mark.parametrize(
        "txt,height", [("abc", 1), ("abc\ndef", 2), ("abc\n\ndef", 3)]
    )
    def test_cell_resizes_on_input(self, tk_root, txt, height):
        """Ensure that the code cell resizes based on user input."""

        cell = nb.new_markdown_cell()

        markdown_cell = MarkdownCell(cell, parent=tk_root)
        markdown_cell.grid(row=1)
        tk_root.update()

        markdown_cell.textbox.focus_force()

        for c in txt:
            sym = c

            if sym == "\n":
                sym = "Return"

            if sym == "\x08":
                sym = "BackSpace"

            markdown_cell.textbox.event_generate("<KeyPress>", keysym=sym)

        assert markdown_cell.textbox.cget("height") == height
