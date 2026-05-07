# Bookmank

A bookmarks management tool written in Python, with a Tk GUI.

# Building & running

Just clone this repository, `cd` into it and launch `bookmank.py`, as follows. Of course, you need a working **Python** distribution, including the **Tk** module.

```bash
$ git clone github.com/baltasarq/Bookmank
$ cd Bookmank
$ python bookmank.py
```

The app has a straightforward GUI that mainly consists of a tree view and three buttons to the right, _add_, _add section_, and _delete_. Select a node to add ore remove a new list of bookmarks, or a bookmark itself. Double-click a section or bookmark to edit it.

You can invoke the app with a given file as argument, instead of starting from scratch. For instance:

```bash
$ python bookmank.py ~/Docs/bookmarks.html
```

The very same path will be used to save the results when exiting the app. If a file is not given, then it saves to `bms.html` in the current directory.
