import logging
import tkinter as tk
import tkinter.ttk as ttk

logger = logging.getLogger(__name__)


class View(ttk.Frame):
    """A complete 'mini-application' that hopefully will be composable into larger
    apps at some point."""

    def __init__(self, parent, *args, root=None, **kwargs):
        super().__init__(parent, *args, **kwargs)

        if root is not None:
            self.init_menu(root)

        self.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, pad=0)

        self._canvas = tk.Canvas(self)
        self._scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self._canvas.yview
        )

        # Anything that should be part of the scrollable area needs to set self.view
        # as its parent.
        self.view = ttk.Frame(self._canvas)
        self.view.bind("<Configure>", self._resize_view)

        # Allow users to scroll on the view itself.
        self.view.bind_all("<Button-4>", self._on_scroll)
        self.view.bind_all("<Button-5>", self._on_scroll)

        self._canvas.create_window((0, 0), window=self.view, anchor="nw")
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._canvas.grid(row=0, column=0, sticky=tk.N + tk.E + tk.S + tk.W)
        self._canvas.bind("<Configure>", self._resize_canvas)

        self._scrollbar.grid(row=0, column=1, sticky=tk.N + tk.E + tk.S + tk.W)

    def init_menu(self, root):
        """Views should override this if they provide a menubar."""

    def _on_scroll(self, event):
        """Allow the user to scroll the view with the mouse."""
        direction = -1 if event.num == 4 else 1
        self._canvas.yview_scroll(direction, "units")

    def _resize_canvas(self, event):
        logger.debug("Configure: %s", event)

    def _resize_view(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
