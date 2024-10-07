import zlib
import json
import pickle

import worlds
from worlds.AutoWorld import AutoWorldRegister
from worlds.mm_recomp import MMRWorld
from Generate import main as generate_main

# register the Majora's Mask Recompiled world type
# we do this to not rely on AutoWorldRegister's auto-discovery
AutoWorldRegister.world_types = { "Majora's Mask Recompiled":  MMRWorld }

# patch the data package to include our world
worlds.network_data_package = DataPackage = {
    "games": {world_name: world.get_data_package_data() for world_name, world in AutoWorldRegister.world_types.items()},
}

# patch zlib.compress which is used to export the multidata as .archipelago (zip) files
# we'll patch it to instead return a json blob which can be output as a .json file
def produce_json(data, level=None):
    if isinstance(data, bytes):
        try:
            data = pickle.loads(data)
        except pickle.UnpicklingError:
            # If it's not pickled data, we'll leave it as is
            pass

    def default_serializer(obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, tuple):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        return str(obj)

    return json.dumps(data, default=default_serializer, indent=2).encode('utf-8')

zlib.compress = produce_json

# our main function
def main():
  generate_main()
