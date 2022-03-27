from dataclasses import dataclass


@dataclass
class StorageTransferPath:
    local_path: str
    storage_path: str

    def __post_init__(self):
        assert isinstance(self.local_path, str)
        assert isinstance(self.storage_path, str)

    def __str__(self):
        return self.__dict__.__str__()
