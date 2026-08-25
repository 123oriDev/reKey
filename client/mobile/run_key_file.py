class FileKeyHandler:
    """Base class for file key event handlers. Inherit from this to create your own."""

    def header(self, head, key):
        pass

    def no_header(self, line):
        pass


class FileKeyReader:
    """Read key file, delegating actions to a Handler object"""

    def __init__(self, handler: FileKeyHandler, path):
        self.handler = handler
        self._path = path

    def process_line(self, line):
        try:
            split_line = line.split(":", 1)
            split_line[1] = split_line[1][1:-1]

            self.handler.header(split_line[0], split_line[1])
        except Exception:
            self.handler.no_header(line)

    def start(self) -> None:
        with open(self._path, "r") as file:
            for line in file:
                self.process_line(line.strip())


class PrintFileKeyHandler(FileKeyHandler):
    def header(self, head, key):
        print(f"{head}  {key}")

    def no_header(self, line):
        print("noooooo")


def main():
    FileKey = PrintFileKeyHandler()
    FileReader = FileKeyReader(
        handler=FileKey, path=r"C:\Users\Ori\Documents\apps\reKey\test.txt"
    )
    FileReader.start()


if __name__ == "__main__":
    main()
