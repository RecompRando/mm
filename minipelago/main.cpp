#include "utils.h"
#include "import.h"

#include <stdio.h>
#include <dlfcn.h>
#include <Python.h>
#include <filesystem>

#ifdef _WIN32
extern "C" DLLEXPORT u32 recomp_api_version = 1;
#else
extern "C" uint32_t recomp_api_version = 1;
#endif

void generate() {
  auto dylib_path = get_mod_dylib_path();

  Py_Initialize();
  PyRun_SimpleString("import sys");

  // remove last path entry and add the zip file's dep folder based on the current dynamic library path
  PyRun_SimpleString("sys.path.pop()");
  auto mod_zip_path = std::string("sys.path.insert(0, '") + get_mod_zip_path().string() + "')";
  PyRun_SimpleString(mod_zip_path.c_str());
  auto mod_deps_path = std::string("sys.path.insert(0, '") + get_mod_zip_path().string() + "/deps/')";
  PyRun_SimpleString(mod_deps_path.c_str());

  // debug print sys.path
  PyRun_SimpleString("print(sys.path)");

  // Create a Python list to simulate sys.argv
  std::filesystem::path player_files_path = get_mod_folder() / "Players";
  std::vector<std::string> args = {
    "MMGenerate.py",  // argv[0] is typically the script name
    "--player_files_path", player_files_path.string(),
    "--outputpath", get_mod_folder().string()
  };
  
  PyObject* py_argv = PyList_New(args.size());
  for (size_t i = 0; i < args.size(); ++i) {
    PyList_SetItem(py_argv, i, PyUnicode_FromString(args[i].c_str()));
  }

  // Set sys.argv
  PySys_SetObject("argv", py_argv);

  PyRun_SimpleString(
    "from MMGenerate import main as generate\n"
    "generate()"
  );

  Py_DECREF(py_argv);

  // finalize python
  Py_Finalize();
}

extern "C" void bridge_generate(uint8_t* rdram, recomp_context* ctx) {
  generate();
}
