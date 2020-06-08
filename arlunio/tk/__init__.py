import importlib
import logging

from .inspect import Inspector

try:
    import tkinter as tk
    import tkinter.ttk as ttk

    TK = True
except ImportError:
    import unittest.mock as mock

    tk = mock.MagicMock()
    ttk = mock.MagicMock()

    TK = False


class Inspect:
    """Open the arlunio inspector.

    TODO: Add support for notebooks!

    :param module: The module to inspect."""

    def run(self, module: str):
        logger = logging.getLogger(__name__)

        if not TK:
            logger.info(
                "It appears that tkinter is not available on your system but "
                "is required for this command. Please ensure it is available "
                "and try again "
            )
            return 1

        try:
            mod = importlib.import_module(module)
        except ImportError as exc:
            logger.error("Unable to inspect module '%s': %s", module, exc)
            return 1

        root = tk.Tk()
        root.rowconfigure(0, weight=1)
        root.columnconfigure(0, weight=1)

        app = Inspector(mod, root)
        app.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)

        root.title(f"{module} - Arlunio Inspector")
        root.geometry("800x600")
        root.mainloop()
