import clang.cindex as ci
import os.path
import vim
from clang_tools import find_definition

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


def init_clang_tools(library_path):
    """Initialize libclang and tooling."""
    if library_path != "" and not ci.Config.loaded:
        ci.Config.set_library_path(library_path)

    global index
    try:
        index = ci.Index.create()
    except Exception, e:
        print_warning('Failed to load libclang: {}'.format(str(e)))
        return 0

    return 1


def get_tu(filename):
    """Get the translation unit for the given file.

    If it can't be loaded, throw TranslationUnitLoadError"""
    global tus
    global index
    if filename in tus:
        return tus[filename]

    tu = index.parse(filename)
    tus[filename] = tu
    return tu


def reparse_all_tus():
    """Reparse all translation units, using what's in vim's buffers."""
    global tus
    tus_to_reparse = []
    unsaved_files = []
    for b in vim.buffers:
        filename = b.name
        if filename not in tus:
            continue

        tu = get_tu(filename)
        tus_to_reparse.append(tu)
        unsaved_files.append((filename, '\n'.join(b[:len(b)])))

    for tu in tus_to_reparse:
        tu.reparse(unsaved_files)


def go_to_definition(filename, line, col):
    """Find the definition of the symbol under the cursor.

    Return a list of [line, column].
    """
    line = int(line)
    col = int(col)
    print_debug('go_to_definition {}: {}, {}'.format(filename, line, col))

    try:
        tu = get_tu(filename)
    except ci.TranslationUnitLoadError, e:
        print_warning('Could not load "{}": {}'.format(filename, str(e)))
        return [line, col]

    # This should happen asynchronously as files are changed.
    reparse_all_tus()

    ref = find_definition(tu, filename, line, col)
    if ref is None:
        print_warning('No referenced cursor found.')
        return [line, col]

    target_loc = ref.location
    print_debug(target_loc)
    target_file = target_loc.file.name

    if not os.path.samefile(filename, target_file):
        vim.command(':split {}'.format(target_file))

    return [target_loc.line, target_loc.column]
