import logging

from .notebook import NotebookViewer

try:
    import tkinter as tk
    import tkinter.ttk as ttk

    TK = True
except ImportError:
    import unittest.mock as mock

    tk = mock.MagicMock()
    ttk = mock.MagicMock()

    TK = False


logger = logging.getLogger(__name__)


class NbEdit:
    """Launches a simple notebook editor."""

    def run(self):

        if not TK:
            logger.info(
                "It appears that tkinter is not available on your system but "
                "is required for this command. Please ensure it is available "
                "and try again "
            )
            return 1

        root = tk.Tk()
        app = NotebookViewer(root)
        app.mainloop()
