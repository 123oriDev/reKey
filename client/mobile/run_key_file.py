"""Shim — canonical is common/keyfile.py. Keeps `import run_key_file` working."""
import os, sys
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
try:
    from common.keyfile import FileKeyHandler, FileKeyReader, PrintFileKeyHandler
except ImportError:
    class FileKeyHandler:  # type: ignore[no-redef]
        def header(self, head, key): pass
        def no_header(self, line): pass
    class FileKeyReader:  # type: ignore[no-redef]
        def __init__(self, handler, path): self.handler = handler; self._path = path
        def process_line(self, line):
            try:
                split_line = line.split(":", 1)
                split_line[1] = split_line[1][1:-1]
                self.handler.header(split_line[0], split_line[1])
            except Exception: self.handler.no_header(line)
        def start(self):
            with open(self._path, "r") as file:
                for line in file: self.process_line(line.strip())
    class PrintFileKeyHandler(FileKeyHandler):  # type: ignore[no-redef]
        def header(self, head, key): print(f"{head}  {key}")
        def no_header(self, line): print("noooooo")

def main():
    FileKey = PrintFileKeyHandler()
    FileReader = FileKeyReader(handler=FileKey, path=r"C:\Users\Ori\Documents\apps\reKey\tests\try.txt")
    FileReader.start()

if __name__ == "__main__":
    main()
