# (c) 2025 Bookmarks list Baltasar MIT License <baltsarq@gmail.com>


from typing import ClassVar
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Bookmark:
    name: str
    url: str
    parent: object
    NUM: classvar[int] = 0

    def __init__(self, name, url, parent=None):
        Bookmark.NUM += 1

        if not url:
            url = "https://info.cern.ch/"

        name = name.strip()
        if not name:
            dt = datetime.now()
            name = f"name{Bookmark.NUM}-{dt.year:04}{dt:month:02}{dt.day:02}";

        self.name = name
        self.url = url
        self.parent = parent

    def __str__(self):
        return f"{self.name}: {self.url}"


class BookmarkList:
    """A list of bookmarks or other objects BookmarkList"""
    def __init__(self, name="", parent=None, initial_bml=None):
        self._parent = parent
        self._lb = {}

        # Assign a name
        name = name.strip()
        if not name:
            name = f"bookmarklist-{self.level}"

        self._name = name

        # Add the initial elements
        if initial_bml is not None:
            for bm in initial_bml:
                self.add(bm)

    @property
    def level(self):
        """Calculates the nesting level,
           i.e., how many lists are between this list and the top one.
           :return: a number of levels
        """
        toret = 0
        lst = self

        while lst.parent:
            toret += 1
            lst = lst.parent

        return toret

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent: BookmarkList):
        self._parent = new_parent

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    def rename(self, name: str, new_name: str):
        """Renames an item.
            :param name: the current name.
            :param new_name: the new_name.
        """
        if name in self._lb:
            bm = self._lb.get(name)
            del self._lb[name]
            bm._name = new_name
            self.add(bm)

    @property
    def all(self):
        return self._lb.values()

    def get_at_path(self, path: list[str]) -> Bookmark:
        toret = self
        cursor = 0

        while (toret
           and cursor < len(path)
           and isinstance(toret, BookmarkList)):
            toret = toret.get(path[cursor])
            cursor += 1

        if cursor < len(path):
            toret = None

        return toret

    def add(self, bm: {Bookmark|BookmarkList}):
        """Adds a new entry, or a new list of bookmarks"""
        self._lb[bm.name] = bm
        bm.parent = self

    def get(self, name) -> {Bookmark|BookmarkList|None}:
        return self._lb.get(name)

    def delete(self, name: str):
        if name in self._lb:
            del self._lb[name]
            return True

        print("Not deleted")
        return False

    def at(self, i):
        return list(self._lb.values())[i]

    def __getitem__(self, item):
        return self.at(index)

    def __iter__(self):
        return (pair for pair in self._lb.items())

    @property
    def all_names(self):
        return self._lb.keys()

    def __len__(self):
        return len(self._lb)

    def get_str_info(self):
        parent_name = "0"

        if self.parent is not None:
            parent_name = self.parent.name

        return f"'{self.name}' lvl{self.level} #{len(self)} ({parent_name})"

    def __str__(self):
        indent = "    " * self.level
        toret = f"\n{indent}+ {self.get_str_info()}"

        for pair in self:
            bml = pair[1]
            indent = "    " * ( self.level + 1)

            if isinstance(bml, Bookmark):
                toret += f"\n{indent}- " + str(bml)
            else:
                toret += str(bml)

        return toret


if __name__ == "__main__":
    b1 = Bookmark("GMail", "http://gmail.com")
    b2 = Bookmark("Youtube", "hhtp://youtube.com")
    bml1 = BookmarkList("", None, [b1, b2])
    bml2 = BookmarkList()
    bml2.add(b1)
    bml2.add(b2)
    print(b1)
    print(b2)
    print(bml1)
    print(bml2)
