from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class CpuinfoConan(ConanFile):
    name = "cpuinfo"
    description = "CPU INFOrmation library (x86/x86-64/ARM/ARM64, Linux/Windows/Android/macOS/iOS)"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pytorch/cpuinfo"
    license = "BSD-2"
    topics = ("conan", "cpuinfo", "cpu", "pytorch")
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake", "cmake_find_package"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        
    def requirements(self):
        pass
        #self.requires("cloc")
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        if "patches" in self.conan_data:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_SYSTEM_NAME"] = self.settings.os
        cmake.definitions["CMAKE_SYSTEM_PROCESSOR"] = self.settings.arch
        cmake.definitions["CPUINFO_LIBRARY_TYPE"] = "default" # (shared, static, or default) to build
        cmake.definitions["CPUINFO_RUNTIME_TYPE"] = "default" # (shared, static, or default) to use
        cmake.definitions["CPUINFO_LOG_LEVEL"] = "default"    # (info, debug, warning, error, fatal, none or default)
        cmake.definitions["CPUINFO_BUILD_TOOLS"] = True       # isa-info, cpu-info, cache-info, auxv-dump, cpuinfo-dump & cpuid-dump
        cmake.definitions["CPUINFO_BUILD_UNIT_TESTS"] = False
        cmake.definitions["CPUINFO_BUILD_MOCK_TESTS"] = False
        cmake.definitions["CPUINFO_BUILD_BENCHMARKS"] = False
        cmake.definitions["CLOG_RUNTIME_TYPE"] = "default"    # (shared, static, or default) to use
        cmake.definitions["CLOG_BUILD_TESTS"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "Android"]:
            self.cpp_info.system_libs.extend(["pthread"])
