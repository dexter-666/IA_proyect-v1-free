"""JARVIS Beta — custom importer for .pyc-only distribution."""
import importlib.machinery, importlib.util, sys, pathlib

class _PycFinder(importlib.machinery.FileFinder):
    pass

# Register .pyc as importable source-less modules
_loaders = [(importlib.machinery.SourcelessFileLoader, [".pyc"])]
for i, path_hook in enumerate(sys.path_hooks):
    try:
        if "FileFinder" in str(path_hook):
            sys.path_hooks[i] = importlib.machinery.FileFinder.path_hook(*_loaders,
                (importlib.machinery.SourceFileLoader, [".py"]),
                (importlib.machinery.SourcelessFileLoader, [".pyc"]))
            break
    except Exception:
        pass
sys.path_importer_cache.clear()
