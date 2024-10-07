import sys
import os
import shutil

site_packages = sys.path[-1]
output_path = sys.argv[1]
package_folder = os.path.join(output_path, "python")
print(f"Packaging MMRecompRando to {package_folder}")

# Create the main package folder
os.makedirs(package_folder, exist_ok=True)

# Function to copy a file
def copy_file(src, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(src, dest)

# Copy main files
copy_file("archipelago/BaseClasses.py", os.path.join(package_folder, "BaseClasses.py"))
copy_file("archipelago/Generate.py", os.path.join(package_folder, "Generate.py"))
copy_file("archipelago/Fill.py", os.path.join(package_folder, "Fill.py"))
copy_file("archipelago/Main.py", os.path.join(package_folder, "Main.py"))
copy_file("scripts/DummyModuleUpdate.py", os.path.join(package_folder, "ModuleUpdate.py"))
copy_file("archipelago/MultiServer.py", os.path.join(package_folder, "MultiServer.py"))
copy_file("archipelago/NetUtils.py", os.path.join(package_folder, "NetUtils.py"))
copy_file("archipelago/Options.py", os.path.join(package_folder, "Options.py"))
copy_file("archipelago/Utils.py", os.path.join(package_folder, "Utils.py"))
copy_file("archipelago/settings.py", os.path.join(package_folder, "settings.py"))
copy_file("archipelago/requirements.txt", os.path.join(package_folder, "requirements.txt"))
copy_file("scripts/MMGenerate.py", os.path.join(package_folder, "MMGenerate.py"))

# Copy worlds files
copy_file("scripts/worlds_init.py", os.path.join(package_folder, "worlds", "__init__.py"))
copy_file("archipelago/worlds/AutoSNIClient.py", os.path.join(package_folder, "worlds", "AutoSNIClient.py"))
copy_file("archipelago/worlds/AutoWorld.py", os.path.join(package_folder, "worlds", "AutoWorld.py"))
copy_file("archipelago/worlds/Files.py", os.path.join(package_folder, "worlds", "Files.py"))
copy_file("archipelago/worlds/LauncherComponents.py", os.path.join(package_folder, "worlds", "LauncherComponents.py"))
copy_file("archipelago/worlds/alttp/EntranceRandomizer.py", os.path.join(package_folder, "worlds", "alttp", "EntranceRandomizer.py"))
copy_file("archipelago/worlds/alttp/Text.py", os.path.join(package_folder, "worlds", "alttp", "Text.py"))
copy_file("scripts/__init__.py", os.path.join(package_folder, "worlds", "alttp", "__init__.py"))

# Copy necessary worlds
for world in ["generic", "mm_recomp"]:
    world_root = os.path.join("archipelago", "worlds", world)
    for root, dirs, files in os.walk(world_root):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, world_root)
            if rel_path.startswith("docs/") or rel_path.startswith("test/"):
                continue

            dest_path = os.path.join(package_folder, "worlds", world, rel_path)
            copy_file(full_path, dest_path)

# Copy necessary dependencies
for package in ["typing_extensions.py", "yaml", "schema.py", "websockets"]:
    package_root = os.path.join(site_packages, package)
    if package.endswith(".py"):
        copy_file(package_root, os.path.join(package_folder, "deps", package))
    else:
        for root, dirs, files in os.walk(package_root):
            for file in files:
                if not file.endswith(".pyc"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, package_root)
                    dest_path = os.path.join(package_folder, "deps", package, rel_path)
                    copy_file(full_path, dest_path)

print(f"Packaging complete. Files are in {package_folder}")
