# Direct copy of worlds/__init__.py but handles loading worlds when your script is running from within a zip archive
# It would be nice to be able to just replace the parts we need, and while we could patch WorldSource.load,
# we can't patch the freeform code at the end of the file. So we have to copy the whole thing.

import importlib
import os
import sys
import warnings
import zipimport
import zipfile
import time
import dataclasses
from typing import Dict, List, TypedDict, Optional

from Utils import local_path, user_path

local_folder = os.path.dirname(__file__)
user_folder = user_path("worlds") if user_path() != local_path() else None

__all__ = {
    "network_data_package",
    "AutoWorldRegister",
    "world_sources",
    "local_folder",
    "user_folder",
    "GamesPackage",
    "DataPackage",
    "failed_world_loads",
}


failed_world_loads: List[str] = []


class GamesPackage(TypedDict, total=False):
    item_name_groups: Dict[str, List[str]]
    item_name_to_id: Dict[str, int]
    location_name_groups: Dict[str, List[str]]
    location_name_to_id: Dict[str, int]
    checksum: str
    version: int  # TODO: Remove support after per game data packages API change.


class DataPackage(TypedDict):
    games: Dict[str, GamesPackage]


@dataclasses.dataclass(order=True)
class WorldSource:
    path: str  # typically relative path from this module
    is_zip: bool = False
    relative: bool = True  # relative to regular world import folder
    time_taken: Optional[float] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.path}, is_zip={self.is_zip}, relative={self.relative})"

    @property
    def resolved_path(self) -> str:
        if self.relative:
            return os.path.join(local_folder, self.path)
        return self.path

    def load(self) -> bool:
        import traceback
        traceback.print_stack()

        try:
            start = time.perf_counter()
            if self.is_zip:
                if ".zip" in self.resolved_path:
                    path_to_zip = self.resolved_path.split(".zip")[0] + ".zip/worlds"
                    importer = zipimport.zipimporter(path_to_zip)
                    # load with path that's everything after the zip file name
                    importer.load_module(self.path)
                else:
                    importer = zipimport.zipimporter(self.resolved_path)

                if hasattr(importer, "find_spec"):  # new in Python 3.10
                    spec = importer.find_spec(os.path.basename(self.path).rsplit(".", 1)[0])
                    assert spec, f"{self.path} is not a loadable module"
                    mod = importlib.util.module_from_spec(spec)
                else:  # TODO: remove with 3.8 support
                    mod = importer.load_module(os.path.basename(self.path).rsplit(".", 1)[0])

                mod.__package__ = f"worlds.{mod.__package__}"
                mod.__name__ = f"worlds.{mod.__name__}"
                sys.modules[mod.__name__] = mod
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="__package__ != __spec__.parent")
                    # Found no equivalent for < 3.10
                    if hasattr(importer, "exec_module"):
                        importer.exec_module(mod)
            else:
                importlib.import_module(f".{self.path}", "worlds")
            self.time_taken = time.perf_counter()-start
            return True

        except Exception:
            # A single world failing can still mean enough is working for the user, log and carry on
            import traceback
            import io
            file_like = io.StringIO()
            print(f"Could not load world {self}:", file=file_like)
            traceback.print_exc(file=file_like)
            file_like.seek(0)
            import logging
            logging.exception(file_like.read())
            failed_world_loads.append(os.path.basename(self.path).rsplit(".", 1)[0])
            return False

# Function to load worlds from a folder or a zip file within that folder
def load_worlds_from_folder(folder: str, relative: bool):
    for entry in os.scandir(folder):
        if not entry.name.startswith(("_", ".")):
            file_name = entry.name if relative else os.path.join(folder, entry.name)
            if entry.is_dir():
                world_sources.append(WorldSource(file_name, relative=relative))
            elif entry.is_file() and entry.name.endswith(".apworld"):
                world_sources.append(WorldSource(file_name, is_zip=True, relative=relative))

# Function to load worlds when AP is running from within a zip archive
def load_worlds_from_zip(zip_file: str):
    zip_file = zip_file.split(".zip")[0] + ".zip"
    with zipfile.ZipFile(zip_file, 'r') as z:
        for file_name in z.namelist():
            if not file_name.startswith("worlds/"):
                continue
            file_name = file_name.split("worlds/")[1]
            if not file_name.startswith(("_", ".")):
                world_sources.append(WorldSource(file_name, is_zip=True, relative=True))

# find potential world containers, currently folders and zip-importable .apworld's
world_sources: List[WorldSource] = []
for folder in (folder for folder in (user_folder, local_folder) if folder):
    if ".zip" in folder:
        load_worlds_from_zip(folder)
    else:
        relative = folder == local_folder
        load_worlds_from_folder(folder, relative)

# import all submodules to trigger AutoWorldRegister
world_sources.sort()
for world_source in world_sources:
    world_source.load()

# Build the data package for each game.
from .AutoWorld import AutoWorldRegister

network_data_package: DataPackage = {
    "games": {world_name: world.get_data_package_data() for world_name, world in AutoWorldRegister.world_types.items()},
}
