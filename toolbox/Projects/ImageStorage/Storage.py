from typing import Dict, List, Type, Optional
from pathlib import Path
from collections import OrderedDict
import time

from toolbox.DataModels import BaseModel
from toolbox.Context import ContextCli
from toolbox.utils.utils import float_or_none, get_logger

logger = get_logger("ImageStorage")



class File:
    def __init__(self, path: Path):
        self.path = path
        self.bytes: int = path.stat().st_size
        self.creation_time: int = path.stat().st_mtime


class Storage:
    """Manage a local file storage and update its state in a context broker.
    """

    def __init__(self, config: dict, data_model_cls: Type[BaseModel]):
        """
        Args:
            config (dict): Configuration dict.
            data_model_cls (Type[BaseModel]): Base data model to upload to the
                context broker.
        """
        # Parse config
        self._path = Path(config["api"]["storage_path"])
        self._max_n_files = float_or_none(config["api"]["max_n_files"])
        self._max_dir_size = float_or_none(config["api"]["max_dir_size"])
        self._max_file_time = float_or_none(config["api"]["max_file_time"])
        self._delete_from_broker = config["api"]["delete_from_broker"]

        self._context_cli = ContextCli(**config["context_broker"])
        self._path.mkdir(exist_ok=True, parents=True)
        self._stored_files: Dict[str, File] = OrderedDict()
        self._total_size: int = 0

        logger.info(f"Using storage path {self._path}")
    
    def initialize(self):
        """Initialize the file record with the files already present on the
        storage path.
        """
        files = sorted(self._path.iterdir(), key=lambda x: x.stat().st_mtime)
        if files:
            logger.info(f"Initializing storage with the files in {self._path}")
            for f in files:
                entity_id = f.stem.replace(";", ":")
                self.add_file(f, key=entity_id)
    
    def check_dir_limits(self):
        """Check the limits of the storage dir.
        """
        # Maximum number of files
        if self._max_n_files is not None:
            n_files = len(self)
            if n_files > self._max_n_files:
                keys = self.keys()
                for i in range(int(n_files - self._max_n_files)):
                    logger.info(f"Maximum number of files reached ({n_files})")
                    self.delete_file(keys[i])
        
        # Maximum dir size
        if self._max_dir_size is not None:
            if self.total_size > self._max_dir_size:
                keys = self.keys()
                for k in keys:
                    logger.info(f"Maximum directory size reached " \
                        f"({self.total_size})")
                    self.delete_file(k)
                    if self.total_size <= self._max_dir_size:
                        break

    def check_files_time(self):
        """Check the maximum time of the files.
        """
        ct = time.time()
        for k, f in self._stored_files.items():
            if f.creation_time < ct - self._max_file_time:
                logger.info(f"Maximum file time exceeded " \
                    f"({self._max_file_time}s)")
                self.delete_file(k)

    def add_file(
        self,
        path: Path,
        data_model: Optional[Type[BaseModel]] = None,
        key: Optional[str] = None):
        """Add an existing file.

        Args:
            path (Path): Path to the file.
            data_model (Optional[Type[BaseModel]]): A data model object
                representing the file to upload to the context broker. If None,
                no data model will be uploaded to the context broker. Defaults
                to None.
            key (Optional[str]): Optional key to use if no data model is
                provided, otherwise is ignored. Defaults to None.

        Raises:
            ValueError: If key already exists or it is None.
            FileNotFoundError: If file does not exist.
        """
        key = data_model.id if data_model is not None else key
        if key is None:
            raise ValueError("File key can not be None.")
        if key in self._stored_files:
            raise ValueError(
                f"Key {key} already exists ({list(self._stored_files.keys())})"
            )
        if not path.exists():
            raise FileNotFoundError(f"File {path} does not exist")
        logger.info(f"Adding file {path}")
        self._stored_files[key] = File(path)
        self._total_size += self._stored_files[key].bytes
        if data_model is not None:
            self._context_cli.post_data_model(data_model)
    
    def delete_file(self, key: str):
        """Delete a file permanently.

        Args:
            key (str): The file key.
        """
        file = self._stored_files.pop(key)
        logger.info(f"Deleting file {file.path}")
        file.path.unlink(True)
        self._total_size -= file.bytes
        if self._delete_from_broker:
            self._context_cli.delete_entity(key)
    
    def delete_all(self):
        """Delete all the inserted file.
        """
        logger.info("Deleting all the current files")
        for k in self.keys():
            self.delete_file(k)

    def keys(self) -> List[str]:
        """Return an ordered list with the file keys in insertion order.
        """
        return list(self._stored_files.keys())

    def get_file_path(self, filename: str) -> Path:
        """Get the storage file path from a filename.

        Args:
            filename (str)

        Returns:
            Path
        """
        assert ";" not in filename, filename
        return self._path.joinpath(filename.replace(":", ";"))

    @property
    def path(self) -> Path:
        """Returns the storage path.
        """
        return self._path

    @property
    def total_size(self) -> int:
        """Return the total size of the stored files.
        """
        return self._total_size

    def __getitem__(self, key: str) -> Path:
        """Return the path of a file by its key.
        """
        return self._stored_files[key].path
    
    def __len__(self):
        """Return the number of stored files.
        """
        return len(self._stored_files)
    
    def __contains__(self, key: str) -> bool:
        """Return True if the key exists. 
        """
        return key in self._stored_files