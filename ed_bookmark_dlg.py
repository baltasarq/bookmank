# EdBookmarkDlg (c) 2025 Baltasar MIT License <baltsarq@gmail.com>


import tkinter as tk
from tkinter import ttk


class EdBookmarkDlg(tk.Toplevel):
    def __init__(self, parent, bm: Bookmark, title="Add Item"):
        super().__init__(parent)
        self._bm = bm
        self.result = None
        self.transient(parent)
        self.title(title)

        # Build the dialog
        self.update_idletasks()
        width, height = 400, 200
        self.minsize(width, height)
        self.maxsize(width * 2, height * 2)
        x = parent.winfo_x() + ((parent.winfo_width() - width) // 2)
        y = parent.winfo_y() + ((parent.winfo_height() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.create_widgets()

        # Set modality and focus to name entry
        self.grab_set()
        self.name_entry.focus()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name field
        ttk.Label(main_frame, text="Name:").grid(
                            row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.name_entry = ttk.Entry(main_frame, width=40)
        self.name_entry.grid(row=0, column=1,
                             sticky=(tk.W, tk.E), pady=(0, 15), padx=(10, 0))
        self.name_entry.insert(0, self._bm.name)

        # URL field
        ttk.Label(main_frame, text="URL:").grid(
                            row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(main_frame, width=40)
        self.url_entry.grid(row=1, column=1,
                            sticky=(tk.W, tk.E), pady=(0, 15), padx=(10, 0))
        self.url_entry.insert(0, self._bm.url)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(button_frame, text="OK", command=self._on_ok_clk).pack(
                                                    side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel_clk).pack(
                                                    side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)
        self.name_entry.bind("<Return>", lambda e: self.url_entry.focus())
        self.url_entry.bind("<Return>", lambda e: self._on_ok_clk())
        self.bind("<Escape>", lambda e: self._on_cancel_clk())

    def _on_ok_clk(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()

        if not name or not url:
            return  # Don't close if fields are empty

        self.result = (name, url)
        self.destroy()

    def _on_cancel_clk(self):
        self.result = None
        self.destroy()

    def get_result(self):
        """Returns (name, url) tuple or None if cancelled"""
        self.wait_window()
        return self.result


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Window")
    root.geometry("300x200")

    def show_dialog():
        dialog = EdBookmarkDlg(root, "Add New Item")
        result = dialog.get_result()

        if result:
            name, url = result
            print(f"Name: {name}, URL: {url}")
            label.config(text=f"Added: {name}\n{url}")
        else:
            print("Cancelled")
            label.config(text="Cancelled")

    ttk.Button(root, text="Open Dialog", command=show_dialog).pack(pady=20)
    label = ttk.Label(root, text="No item added yet")
    label.pack(pady=10)

    root.mainloop()
