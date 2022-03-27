class DirectoryNotFoundException(Exception):
    """Raised when a directory does not exist"""

    def __init__(self, message):
        super().__init__(message)


class FileNotFoundException(Exception):
    """Raised when no file not found at storage"""

    def __init__(self, message):
        super().__init__(message)
