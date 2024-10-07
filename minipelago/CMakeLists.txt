cmake_minimum_required(VERSION 3.20)

project(minipelago LANGUAGES C CXX)
set(CMAKE_C_STANDARD 17)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(minipelago SHARED ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp ${CMAKE_CURRENT_SOURCE_DIR}/utils.cpp)

target_include_directories(minipelago PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/lib/N64ModernRuntime/librecomp/include
)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
target_include_directories(minipelago PRIVATE ${Python3_INCLUDE_DIRS})
target_link_libraries(minipelago PRIVATE Python3::Python)

add_custom_target(BuildModZip ALL
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_SOURCE_DIR}/scripts/package_mod.py ${CMAKE_CURRENT_BINARY_DIR}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Packaging mod zip"
    DEPENDS ${CMAKE_SOURCE_DIR}/scripts/package_mod.py
)

add_dependencies(minipelago BuildModZip)
