from local_clang.cindex import *
import vim


def print_debug(message):
    """Print messages out if debugging is enabled."""
    print(message)


def print_warning(message):
    """Print warnings out if warnings are enabled."""
    print(message)


def init_clang_tools(library_path):
    """Initialize libclang and tooling."""
    if library_path != "":
        Config.set_library_path(library_path)

    global index
    try:
        index = Index.create()
    except Exception, e:
        print_warning('Failed to load libclang: {}'.format(str(e)))
        return 0


    return 1
