import os
from conans import ConanFile, CMake, tools


class PdalConan(ConanFile):
    name = "pdal"
    version = "1.8.0"
    description = "PDAL is a C++ BSD library for translating and manipulating point cloud data."
    settings = "os", "compiler", "build_type", "arch"
    source_dir = "gdal-%s" % version
    url = "https://github.com/novolog/conan-pdal"
    license = "BSD"
    exports = "pdal.patch"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    options = {"with_laszip": [True, False]}
    requires = (
        "geos/3.7.0@novolog/stable",
        "gdal/2.3.2@novolog/stable",
        "libcurl/7.56.1@bincrafters/stable",
        "libgeotiff/1.4.2@novolog/stable",
        "OpenSSL/1.0.2p@conan/stable"
        # proj4 ?
        # "laszip/3.1.1@novolog/stable",  # optional todo use option
        # "libxml2/2.9.8@bincrafters/stable",  # optional todo use option
        # "zlib/1.2.11@conan/stable", #optional todo use option
    )

    default_options = {
        "with_laszip": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        source_url = "https://github.com/PDAL/PDAL/archive/%s.tar.gz" % self.version
        tools.get(source_url)

        extracted_dir = "PDAL-%s" % self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _get_shared_lib_file_extension(self):
        if self.settings.os == "Windows":
            return ".lib"
        if self.settings.os == "Linux":
            return ".so"

    def _get_libraries_absolute_paths(self, lib_name, lib_files = None):
        lib_path = self.deps_cpp_info[lib_name].lib_paths[0]
        so_ext = self._get_shared_lib_file_extension()

        if lib_files is None:
            lib_files = self.deps_cpp_info[lib_name].libs

        libs_abs_path = []
        for lib in lib_files:
            abs_path = os.path.join(lib_path, lib) + so_ext
            if os.path.isfile(abs_path):
                libs_abs_path.append(abs_path)

            abs_path = os.path.join(lib_path, "lib" + lib) + so_ext
            if os.path.isfile(abs_path):
                libs_abs_path.append(abs_path)

        return ";".join(libs_abs_path)

    def _configure_deps_paths(self, cmake, lib_name, prefix, lib_files=None):
        cmake.definitions[prefix + "_INCLUDE_DIR"] = self.deps_cpp_info[lib_name].include_paths[0]
        cmake.definitions[prefix + "_LIBRARY"] = self._get_libraries_absolute_paths(lib_name, lib_files)

    def _configure_cmake_laszip_options(self, cmake):
        if self.options.with_laszip:
            cmake.definitions["WITH_LASZIP"] = "ON"
            self._configure_deps_paths(cmake, "laszip", "LASZIP", ["laszip", "laszip_api"])
        else:
            cmake.definitions["WITH_LASZIP"] = "OFF"

    def _configure_cmake(self):
        cmake = CMake(self)

        self._configure_deps_paths(cmake, "gdal", "GDAL")
        self._configure_deps_paths(cmake, "libgeotiff", "GEOTIFF")
        self._configure_cmake_laszip_options(cmake)

        cmake.definitions["WITH_TESTS"] = "OFF"
        cmake.definitions["WITH_EXAMPLES"] = "OFF"
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        tools.patch(base_path=self._source_subfolder, patch_file="pdal.patch")
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        # self.cpp_info.libs = [
        #     "pdal_boost",
        #     "pdal_kazhdan",
        #     "pdal_util",
        #     "pdalcpp"
        # ]




