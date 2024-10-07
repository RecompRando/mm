#ifndef UTILS_H

#include <string>
#include <filesystem>

const char* get_mod_dylib_path();
std::filesystem::path get_mod_zip_path();
std::filesystem::path get_mod_folder();

#endif // UTILS_H