"""This contains the implementation of the tools, without editor-specific code.

For example, the logic for finding a definition of a symbol belongs here, but
the code for navigating there in the editor does not.
"""
import clang.cindex as ci

index = None
tus = dict()
PRINT_DEBUG = False
PRINT_WARNING = False


def print_debug(message):
    """Print messages out if debugging is enabled."""
    if not PRINT_DEBUG:
        return
    print(message)


def print_warning(message):
    """Print warnings out if warnings are enabled."""
    if not PRINT_WARNING:
        return
    print(message)


def cursor_contains(cursor, loc):
    """Return whether the cursor extends around the location."""
    start = cursor.extent.start
    end = cursor.extent.end
    if start.file is None and loc.file is not None:
        return False
    if start.file is not None and loc.file is None:
        return False
    if start.file is not None and loc.file is not None:
        if start.file.name != loc.file.name:
            return False
    if start.line > loc.line:
        return False
    if start.line == loc.line and start.column > loc.column:
        return False
    if end.line < loc.line:
        return False
    if end.line == loc.line and end.column < end.column:
        return False
    return True


def get_cursors_containing(cursor, loc, cursors=None):
    """Return a list of child cursors that extend around the location.

    If cursors (a list) is passed in, cursors will be appended to it.
    Unexposed cursors will be ignored.
    """
    if cursors is None:
        cursors = []
    if not cursor_contains(cursor, loc):
        return cursors
    if cursor.kind != ci.CursorKind.UNEXPOSED_EXPR:
        cursors.append(cursor)

    for child in cursor.get_children():
        get_cursors_containing(child, loc, cursors)

    return cursors


def get_smallest_cursor_containing(cursor, loc):
    """Return the shortest child cursor containing the location."""
    cursors = get_cursors_containing(cursor, loc)

    if not cursors:
        return None

    return min(cursors,
               key=lambda c: c.extent.end.offset - c.extent.start.offset)


def find_cursor_at_pos(tu, filename, line, col):
    """Find the cursor in the translation unit containing the position."""
    loc = tu.get_location(filename, (line, col))
    return get_smallest_cursor_containing(tu.cursor, loc)


def find_definition(tu, filename, line, col, tus=None):
    """Find the definition of the symbol at the given position.

    Return None if it cannot be found."""


def find_all_definitions(cursor):
    """Find all definitions that are children of the cursor.

    The returned definitions will be a dict of cursors, keyed by their USR.
    """
    def visitor(child, parent, acc_defns):
        if child.is_definition():
            acc_defns[child.get_usr()] = child
        # Recurse.
        return 2

    defns = dict()
    ci.conf.lib.clang_visitChildren(cursor,
                                    ci.callbacks['cursor_visit'](visitor),
                                    defns)

    return defns


class CrossTUIndex:
    """Index and cache across translation units."""

    def __init__(self):
        self.index = ci.Index.create()
        self.tus = dict()

    def get_or_parse_tu(self, filename):
        """Get the translation unit, parsing it if it's not already loaded.

        If it can't be loaded, throw TranslationUnitLoadError."""
        try:
            return self.tus[filename]
        except KeyError:
            # This can throw TranslationUnitLoadError.
            tu = self.index.parse(filename)
            self.tus[filename] = tu
            return tu

    def parse_tu(self, filename):
        """Parse the new translation unit.

        It must not already be loaded. If it can't be loaded, throw
        TranslationUnitLoadError.
        """
        assert filename not in self.tus
        tu = self.index.parse(filename)
        self.tus[filename] = tu
        return tu

    def find_definition(self, filename, line, col):
        """Find the definition of the symbol at the given position.

        Return None if it cannot be found.
        """
        try:
            cursor = find_cursor_at_pos(self.tus[filename],
                                        filename, line, col)
        except KeyError:
            return None

        if cursor is None:
            return None

        if cursor.referenced is None:
            return None

        # If the definition is in this TU, return it immediately.
        if cursor.referenced.is_definition():
            return cursor.referenced

        # Otherwise we need to go searching in other TUs.
        if not self.tus:
            return cursor.referenced

        usr = cursor.referenced.get_usr()
        for tu in self.tus.itervalues():
            defns = find_all_definitions(tu.cursor)
            if usr in defns:
                return defns[usr]

        # Fall back on a declaration, if it can be found.
        return cursor.referenced
