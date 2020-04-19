from conans import ConanFile, CMake, tools
import shutil
import os

class ClogConan(ConanFile):
    name = "clog"
    description = "C-style library for logging errors, warnings, information " \
                  "notes, and debug information."
    license = "BSD-2-Clause"
    topics = ("conan", "clog", "logging", "cpuinfo")
    homepage = "https://github.com/pytorch/cpuinfo/tree/master/deps/clog"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "logto" : ["stdio", "android"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "logto": "stdio"
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os != "Android":
            del self.options.logto

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        commit = os.path.splitext(os.path.basename(self.conan_data["sources"][self.version]["url"]))[0]
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "cpuinfo-" + commit
        shutil.move(os.path.join(extracted_dir, "deps/clog"), self._source_subfolder)
        shutil.rmtree(extracted_dir)
    
    # Type of (MSVC) runtime library (shared, static, or default) to use 
    def _clog_runtime(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            if "MTd" in self.settings.compiler.runtime:
                return "static"
            elif "MDd" in self.settings.compiler.runtime:
                return "dynamic"
            else:
                return "default"
        else:
            return "default"

    def _patch_sources(self):
        if "patches" in self.conan_data:
            for patch in self.conan_data["patches"][self.version]:
                tools.patch(**patch)
        
    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CLOG_RUNTIME_TYPE"] = self._clog_runtime()
        if self.settings.os == "Android":
            self._cmake.definitions["CLOG_LOG_TO_STDIO"] = True if self.options.logto == "stdio" else False
        self._cmake.definitions["CLOG_BUILD_TESTS"] = False
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake
    
    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Android":
            self.cpp_info.system_libs = ["log"]
