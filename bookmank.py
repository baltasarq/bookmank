# Bookmank (c) 2025 Baltasar MIT License <baltsarq@gmail.com>


import sys
import logging
import tkinter as tk
import tkinter.simpledialog
import tkinter.ttk as ttk
from tkinter import simpledialog

from ed_bookmark_dlg import EdBookmarkDlg

from core.bookmark_list import Bookmark
from core.bookmark_list import BookmarkList
from core.bookmark_persistent import PersistentBookmarks


log = logging.getLogger(__name__)
logging.basicConfig(filename="bookmank.log", level=logging.INFO)


class BookMarkListTreeView(ttk.Treeview):
    """Customized tree view for a bookmark list."""
    def __init__(self, master, bml: BookmarkList, dbl_click_fn):
        super().__init__(master=master, columns=("url"))
        self._bml = bml
        self._dbl_click_fn = dbl_click_fn
        self.bind("<Double-1>", self._dbl_click)
        self.heading("#0", text="Name")
        self.heading("url", text="URL")
        self.update()

    @property
    def bookmark_list(self) -> BookmarkList:
        return self._bml

    @bookmark_list.setter
    def bookmark_list(self, bml: BookmarkList):
        self._bml = bml
        self.update()

    def _dbl_click(self, evt):
        """Handles double-clicking a cell."""
        row = self.identify_row(evt.y)
        col = self.identify_column(evt.x)
        path = self._get_item_path(row)
        self._dbl_click_fn(path, row, col)

    def _add_bm_to_tree(self, node_id: str, bm: Bookmark):
        """Adds a given Bookmark to the tree under the node_id node.
            :param node_id: the node under which the bookmark will hang,
            :oaram bm: a given Bookmark.
        """
        self.insert(node_id, tk.END, text=bm.name, values=[bm.url])

    def _add_bm_list_to_tree(self, node_id: str, bml: BookmarkList):
        """Adds a whole  BookmarkList under the given node with id node_id-
            :param node_id: the id of the node under which the list will hang.
            :bml: a BookmarkList.
        """
        for pair in bml:
            bm = pair[1]

            # Is it a list? Then, recurse
            if isinstance(bm, BookmarkList):
                subnode_id = self.insert(node_id, tk.END, text=bm.name)
                self._add_bm_list_to_tree(subnode_id, bm)
            else:
                # Add bookmark
                self._add_bm_to_tree(node_id, bm)

    def _expand(self, node_id: str):
        """Expands the whole tree under the given node with id node_id.
            :param node_is: the id of the node to expand.
        """
        self.item(node_id, open=True)
        for subnode_id in self.get_children(node_id):
            self._expand(subnode_id)

    def _get_item_path(self, node_id: str) -> list[str]:
        """Returns the full path to an item as a list.
            :return: a list of text, in which item is a name.
        """
        toret = []

        while node_id:
            toret.insert(0, self.item(node_id)["text"])
            node_id = self.parent(node_id)

        return toret

    def _get_focused_item_path(self) -> list[str]:
        """Returns the full path of the focused item.
            :return: a list of names.
        """
        return self._get_item_path(self.focus())

    def _get_focused_bookmark(self) -> {Bookmark|BookmarkList}:
        toret = None
        path = self._get_focused_item_path()

        if path:
            path = path[1:]
            toret = self._bml.get_at_path(path)

        return toret

    def _get_focused_bookmark_list(self) -> {BookmarkList}:
        toret = self._get_focused_bookmark()

        if toret is not None:
            if not isinstance(toret, BookmarkList):
                toret = toret.parent
        else:
            toret = self._bml

        return toret

    def update(self):
        if not self.bookmark_list:
            return

        self.delete(*self.get_children())
        self._tv_root_id = self.insert('', tk.END, text='Bookmarks')
        self._add_bm_list_to_tree(self._tv_root_id, self.bookmark_list)
        self._expand(self._tv_root_id)


class TopLevelWindow:
    def __init__(self, toplevel: tk.Toplevel, path: str):
        self._path = path
        self._bms = TopLevelWindow._load_bms(path)
        self._tk = toplevel
        self._tk.minsize(600, 400)
        self._tk.title("Bookmank")
        self._tk.bind("<Destroy>", lambda evt: self._on_close())
        self._tree = BookMarkListTreeView(
                        self._tk,
                        self._bms,
                        lambda p, r, c: self._on_tv_double_click(p, r, c))
        self._tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT, pady=10, padx=10)
        self._frm = ttk.Frame(self._tk)
        self._bt_add = ttk.Button(self._frm, text="Add")
        self._bt_add.pack(padx=10, pady=10)
        self._bt_add.bind("<Button-1>", self._on_add)
        self._bt_add_sect = ttk.Button(self._frm, text="Add section")
        self._bt_add_sect.bind("<Button-1>", self._on_add_sect)
        self._bt_add_sect.pack(padx=10, pady=10)
        self._bt_del = ttk.Button(self._frm, text="Delete")
        self._bt_del.bind("<Button-1>", self._on_del)
        self._bt_del.pack(padx=10, pady=10)
        self._frm.pack(fill=tk.Y, side=tk.RIGHT)
        self._tree.update()

    @staticmethod
    def _load_bms(path: str) -> BookmarkList:
        try:
            toret = PersistentBookmarks.load(path)
        except IOError as exc:
            log.info(f"Starting blank, since path does not exist: `{path}`")
            toret = BookmarkList("Bookmarks")

        return toret

    def _edit_bookmark(self, bm: Bookmark):
        result = EdBookmarkDlg(self._tk, bm, f"Modify: {bm.name}").get_result()

        if result:
            bml = bm.parent
            bml.delete(bm.name)
            bml.add(Bookmark(result[0], result[1]))
            self._tree.update()

    def _edit_bookmarklist(self, bml: BookmarkList):
        new_name = tk.simpledialog.askstring("New name", "Name", initialvalue=bml.name)

        if new_name:
            bml.parent.rename(bml.name, new_name)
            self._tree.update()

    def _on_tv_double_click(self, path, row, col):
        log.info(f"Editing path: {path}")
        bm = self._bms.get_at_path(path[1:])
        log.info(f"found bm: {bm}")

        if bm is None:
            log.warning(f"Missing: bookmark: {path}")
            return

        # Is it a list?
        if isinstance(bm, BookmarkList):
            self._edit_bookmarklist(bm)
        else:
            self._edit_bookmark(bm)

    def _on_add(self, evt):
        bm = Bookmark("name", "http://url.com")
        result = EdBookmarkDlg(self._tk, bm, "Add bookmark").get_result()

        if result:
            bml = self._tree._get_focused_bookmark_list()
            bml.add(Bookmark(result[0], result[1]))
            self._tree.update()

    def _on_add_sect(self, evt):
        name = tk.simpledialog.askstring("New section", "section")

        if name:
            bml = self._tree._get_focused_bookmark_list()
            bml.add(BookmarkList(name))
            self._tree.update()

    def _on_del(self, evt):
        bm = self._tree._get_focused_bookmark()

        if bm is None:
            log.warning(f"missing a bookmark for deletion")
            return

        bm.parent.delete(bm.name)
        self._tree.update()

    def run(self):
        self._tk.mainloop()

    def _on_close(self):
        self._tk.withdraw()
        log.info(f"Writing to: `{path}`")
        PersistentBookmarks(self._bms).save(self._path)


if __name__ == "__main__":
    path = "bms.html"
    if len(sys.argv) > 1:
        path = sys.argv[-1]

    tlw = TopLevelWindow(tk.Tk(), path)
    tlw.run()
