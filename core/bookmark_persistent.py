# (c) 2025 Bookmarks persistent Baltasar MIT License <baltsarq@gmail.com>


from datetime import datetime
from enum import Enum, auto
from html.parser import HTMLParser
import logging


from core.bookmark_list import Bookmark
from core.bookmark_list import BookmarkList


log = logging.getLogger(__name__)
logging.basicConfig(filename="bookmank.log", level=logging.INFO)


class BookmarksFileParser(HTMLParser):
    """Parses a bookmarks file."""
    class Status(Enum):
        """State for the finite machine."""
        TOP_LEVEL = auto()
        READ_ENTRY = auto()
        READ_NAME = auto()
        READ_BOOKMARK = auto()

    def __init__(self):
        super().__init__()
        self._bms = self._curr = None
        self._status = BookmarksFileParser.Status.TOP_LEVEL
        self._current_name = "Bookmarks"
        log.info("BookmarksFileParser.init")
        log.debug(f"{self._curr=}")

    @property
    def bookmark_list(self):
        return self._bms

    def handle_starttag(self, tag, attrs):
        log.info(f"*** RECEIVED TAG: {tag} with {attrs}")
        match tag.lower():
            case "dl":
                new_list = BookmarkList(self._current_name, self._curr)

                if self._bms is None:
                    self._bms = new_list

                if self._curr is not None:
                    self._curr.add(new_list)

                self._curr = new_list
                log.info(f"Created new list: {self._curr=}")
                log.info(f"Previous list: {self._curr.parent=}")
                self._status = BookmarksFileParser.Status.TOP_LEVEL
            case "dt":
                self._status = BookmarksFileParser.Status.READ_ENTRY
                log.info(f"Status: {self._status}")
            case "h3":
                self._status = BookmarksFileParser.Status.READ_NAME
                log.info(f"Status: {self._status}")
            case "a":
                log.info("Preparing to read bookmark")
                self._status = BookmarksFileParser.Status.READ_BOOKMARK
                href = [v for (k, v) in attrs if k == "href"]
                if len(href) < 1:
                    raise Exception("couldn't find HREF in a")
                self._url = href[0]
                log.debug(f"{self._url=}")
                log.info(f"Status: {self._status}")


    def handle_endtag(self, tag):
        log.info(f"*** TAG ENDS: {tag}")
        match tag.lower():
            case "dl":
                log.info(f"Status: {self._status}")
                if self._curr is not None and self._curr.parent is not None:
                    self._curr = self._curr.parent
                log.info(f"Status: {self._status}")
                log.debug(f"{self._curr=}")
                self._status = BookmarksFileParser.Status.TOP_LEVEL
            case "h3", "dt":
                self._status = BookmarksFileParser.Status.TOP_LEVEL

    def handle_data(self, data):
        data = data.strip()
        log.info(f"*** RECEIVED data: `{data}`")

        if data:
            match self._status:
                case BookmarksFileParser.Status.READ_NAME:
                    log.info(f"Set bookmark list title: " + data)
                    log.debug(f"{self._curr}")
                    self._current_name = data
                case BookmarksFileParser.Status.READ_BOOKMARK:
                    log.info(f"Create new bookmark: `{data}`/`{self._url}`")
                    self._curr.add(Bookmark(data, self._url))


class PersistentBookmarks:
    """Persistence for bookmarks, read/write."""
    INDENT = "    "

    def __init__(self, bms: BookmarkList):
        """Creates a new saving PersistentBookmarks.
            :param bms: a bookmarks list
        """
        self._bms = bms

    @property
    def bookmark_list(self) -> BookmarkList:
        return self._bms

    def save(self, nf: str):
        """Saves the list of bookmarks.
            :param bf: a path to save the BookmarkList to.
        """
        if self._bms is None:
            return

        with open(nf, "wt") as f:
            PersistentBookmarks.write_headers(f)
            self._save_bms_to(f, 1, self._bms)

    def _save_bms_to(self, f, lvl, bms: BookmarkList):
        """Recursively saves a given BookmarkList.
            :param f: the file to save.
            :param lvl: the indent level.
            :param bms: the BookmarkList to save.
        """
        indent = PersistentBookmarks.INDENT * lvl
        inner_indent = indent + PersistentBookmarks.INDENT
        f.write(f"\n{indent}<dl>\n")
        f.write(f"{indent}<dt><h3>{bms.name}</h3></dt>\n")

        for entry in bms:
            if isinstance(entry[1], BookmarkList):
                self._save_bms_to(f, lvl + 1, entry[1])
            else:
                f.write(f"{inner_indent}<dt><a href=\"{entry[1].url}\">"
                        + f"{entry[0]}</a></dt>\n")
        f.write(f"\n{indent}</dl>\n")

    @staticmethod
    def write_headers(f):
        """Writes the required headers pf the bookmarks file."""
        f.write("<!DOCType NETSCAPE-Bookmark-file-1>\n")
        f.write("<meta http-equiv=\"Content-Type\" ")
        f.write("content=\"text/html;charset=UTF-8\">\n")
        f.write("<title>Bookmarks</title>\n")
        f.write("<h1>Bookmarks</h1>\n\n")

    @staticmethod
    def load(path: str):
        """Loads a BookmarkList object from a given path.
            :param path: the path to a filewith bookmarks  to read and parse.
            :return: the resulting BookmarkList object.
        """
        parser = BookmarksFileParser()

        with open(path, "rt") as f:
            parser.feed(f.read())

        return parser.bookmark_list


if __name__ == "__main__":
    log.info("\n--------\nStarting as program")
    bms = PersistentBookmarks.load("/home/baltasarq/Documents/varios/bookmarks.html")
    PersistentBookmarks(bms).save("bms.html")
    print(bms)
