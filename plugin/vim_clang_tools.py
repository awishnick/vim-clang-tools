import clang.cindex as ci
import os.path
import vim
from clang_tools import CrossTUIndex

index = None
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
        index = CrossTUIndex()
    except Exception, e:
        print_warning('Failed to load libclang: {}'.format(str(e)))
        return 0

    return 1


def reparse_all_tus():
    """Reparse all translation units, using what's in vim's buffers."""
    global index
    tus_to_reparse = []
    unsaved_files = []
    for b in vim.buffers:
        filename = b.name

        try:
            tu = index.tus[filename]
            tus_to_reparse.append(tu)
            unsaved_files.append((filename, '\n'.join(b[:len(b)])))
        except KeyError:
            _, ext = os.path.splitext(filename)
            print_debug('parse_tu {} {}'.format(filename, ext))
            if ext[1:] in ['c', 'cpp', 'h', 'm', 'mm']:
                index.parse_tu(filename)

    for tu in tus_to_reparse:
        tu.reparse(unsaved_files)


def go_to_definition(filename, line, col):
    """Find the definition of the symbol under the cursor.

    Return a list of [line, column].
    """
    line = int(line)
    col = int(col)
    print_debug('go_to_definition {}: {}, {}'.format(filename, line, col))

    # This should happen asynchronously as files are changed.
    reparse_all_tus()

    global index
    ref = index.find_definition(filename, line, col)
    if ref is None:
        print_warning('No referenced cursor found.')
        print_debug(index.tus)
        return [line, col]

    target_loc = ref.location
    print_debug(target_loc)
    target_file = target_loc.file.name

    if not os.path.samefile(filename, target_file):
        vim.command(':split {}'.format(target_file))

    return [target_loc.line, target_loc.column]
