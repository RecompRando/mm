#include "utils.h"

#include <dlfcn.h>

const char* get_mod_dylib_path() {
  Dl_info info;
  dladdr((void*)get_mod_dylib_path, &info);
  return info.dli_fname;
}

std::filesystem::path get_mod_zip_path() {
  auto dylib_path = get_mod_dylib_path();
  std::filesystem::path path(dylib_path);
  path.replace_extension(".zip");

  // on unix platforms the dylib is prefixed as lib, so we'll remove it
  #ifndef _WIN32
  path.replace_filename(path.stem().string().substr(3) + ".zip");
  #endif

  return path;
}

std::filesystem::path get_mod_folder() {
  auto dylib_path = get_mod_dylib_path();
  auto mods_path = std::filesystem::path(dylib_path).parent_path();
  return mods_path;
}
