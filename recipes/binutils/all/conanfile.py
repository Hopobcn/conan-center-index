from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class BinutilsConan(ConanFile):
    name = "binutils"
    description = "A collection of binary tools"
    homepage = "https://sourceware.org/binutils"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "binutils", "ld", "as", "gold")
    exports = "patches/**"
    license = ["GPL-3.0-or-later", "GPL-2.0-or-later"]
    
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False]
    }
    default_options = {
        "shared": False
    }

    generators = "pkg_config"

    _autotools = None
    _source_subfolder = "source_subfolder"


    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        #if self.settings.compiler in ["Visual Studio", "clang", "apple-clang"]:
        #    raise ConanInvalidConfiguration("Compiler %s not supported. "
        #                  "binutils only supports gcc" % self.settings.compiler)
        #if self.settings.compiler != "gcc":
        #    self.output.warn("Compiler %s is not gcc." % self.settings.compiler)

    def requirements(self):
        self.requires("gmp/6.1.2")
        self.requires("mpc/1.1.0")
        self.requires("mpfr/4.0.2")
        self.requires("isl/0.22")

    def build_requirements(self):
        self.build_requires("automake/1.16.2")
        self.build_requires("m4/1.4.18")
        self.build_requires("flex/2.6.4")
        self.build_requires("bison/3.5.3")
        self.build_requires("pkgconf/1.7.3")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
    
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        args = [
            "--enable-shared={}".format("no" if self.options.shared else "yes"),
            "--enable-host-shared={}".format("no" if self.options.shared else "yes"),
            # --with-static-standard-libraries
            "--with-system-zlib",
            '--with-mpc=%s' % self.deps_cpp_info["mpc"].rootpath,
            "--with-mpfr=%s" % self.deps_cpp_info["mpfr"].rootpath,
            "--with-isl=%s" % self.deps_cpp_info["isl"].rootpath,
            "--without-isl"
        ]
        if self.settings.os == "Macos":
            xcrun = tools.XCRun(self.settings)
            args.extend([
                "--with-build-sysroot={}".format(xcrun.sdk_path)
            ])
        
        if tools.cross_building(self.settings):
            if self._autotools.build:
                args.append("--build=%s" % self._autotools.build)
            if self._autotools.host:
                args.append("--host=%s" % self._autotools.host)
            if self._autotools.target:
                args.append("--target=%s" % self._autotools.target)

        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        #for patch in self.conan_data.get("patches", {}).get(self.version, []):
        #    tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv")
        autotools = self._configure_autotools()
        autotools.make()
    
    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        
    def package_info(self):
        # library components
        self.cpp_info.components["libbfd"].libs = ["bfd"]
        self.cpp_info.components["libbfd"].requires = ["gmp::gmp", "mpc::mpc", "mpfr::mpfr", "isl::isl"]

        self.cpp_info.components["libopcodes"].libs = ["opcodes"]
        self.cpp_info.components["libopcodes"].requires = ["libbfd", "gmp::gmp", "mpc::mpc", "mpfr::mpfr", "isl::isl"]

        self.cpp_info.components["libctf-nobfd"].libs = ["ctf-nobfd"]
        self.cpp_info.components["libctf"].libs = ["ctf"]

        # utilities
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        bin_ext = ".exe" if self.settings.os == "Windows" else ""
        
        addr2line = tools.unix_path(os.path.join(self.package_folder, "bin", "addr2line" + bin_ext))
        self.output.info("Setting ADDR2LINE to {}".format(addr2line))
        self.env_info.ADDR2LINE = addr2line

        ar = tools.unix_path(os.path.join(self.package_folder, "bin", "ar" + bin_ext))
        self.output.info("Setting AR to {}".format(ar))
        self.env_info.AR = ar

        nm = tools.unix_path(os.path.join(self.package_folder, "bin", "nm" + bin_ext))
        self.output.info("Setting NM to {}".format(nm))
        self.env_info.NM = nm

        objdump = tools.unix_path(os.path.join(self.package_folder, "bin", "objdump" + bin_ext))
        self.output.info("Setting OBJDUMP to {}".format(objdump))
        self.env_info.OBJDUMP = objdump

        ranlib = tools.unix_path(os.path.join(self.package_folder, "bin", "ranlib" + bin_ext))
        self.output.info("Setting RANLIB to {}".format(ranlib))
        self.env_info.RANLIB = ranlib

        readelf = tools.unix_path(os.path.join(self.package_folder, "bin", "readelf" + bin_ext))
        self.output.info("Setting READELF to {}".format(readelf))
        self.env_info.READELF = readelf

        size = tools.unix_path(os.path.join(self.package_folder, "bin", "size" + bin_ext))
        self.output.info("Setting SIZE to {}".format(size))
        self.env_info.SIZE = size

        strings = tools.unix_path(os.path.join(self.package_folder, "bin", "strings" + bin_ext))
        self.output.info("Setting STRINGS to {}".format(strings))
        self.env_info.STRINGS = strings

        strip = tools.unix_path(os.path.join(self.package_folder, "bin", "strip" + bin_ext))
        self.output.info("Setting STRIP to {}".format(strip))
        self.env_info.STRIP = strip


