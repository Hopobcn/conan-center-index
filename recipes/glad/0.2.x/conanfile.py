import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class GladConan(ConanFile):
    name = "glad"
    description = "Multi-Language Vulkan/GL/GLES/EGL/GLX/WGL Loader-Generator based on the official specs"
    topics = ("conan", "glad", "vulkan", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Dav1dde/glad"
    license = "MIT"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
                
        # APIs 
        "egl": ["None", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
        "gl": [
            "None", 
            "1.0", "1.1", "1.2", "1.3", "1.4", "1.5",
            "2.0", "2.1",
            "3.0", "3.1", "3.2", "3.3",
            "4.0", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6"
        ],
        "gl_profile" : ["compatibility", "core"],
        "gles1": ["None", "1.0"],
        "gles2": ["None", "2.0", "3.0", "3.1", "3.2"],
        "glsc2": ["None", "2.0"],
        "glx": ["None", "1.0", "1.1", "1.2", "1.3", "1.4"],
        "vulkan": ["None", "1.0", "1.1", "1.2"],
        "wgl": ["None", "1.0"],
        "extensions": "ANY", # Path to extensions file or comma separated list of extensions, if missing all extensions are included
        
        # generator options
        "merge": [True, False], # Merge multiple APIs of the same specification into one file
        "quiet": [True, False],

        # internal generator options
        "alias" : [True, False], # Enables function pointer aliasing
        "headeronly": [True, False], # Generate a header only version of glad
        "loader": [True, False], # Include internal loaders for APIs
        "mx": [True, False], # Mimic global GL functions with context switching
        "mxglobal": [True, False],
        "on_demand": [True, False] # On-demand function pointer loading initialize on use [experimental]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        
        "egl": "1.5",
        "gl" : "1.1",
        "gl_profile": "compatibility",
        "gles1": "1.0",
        "gles2": "None",
        "glsc2": "None",
        "glx": "1.4",
        "vulkan": "None",
        "wgl": "None",
        "extensions": "EGL_KHR_cl_event2,EGL_KHR_fence_sync,EGL_KHR_image,EGL_KHR_image_base,EGL_KHR_reusable_sync,GL_ARB_copy_buffer,GL_ARB_fragment_shader,GL_ARB_framebuffer_object,GL_ARB_geometry_shader4,GL_ARB_get_program_binary,GL_ARB_imaging,GL_ARB_multitexture,GL_ARB_separate_shader_objects,GL_ARB_shader_objects,GL_ARB_shading_language_100,GL_ARB_texture_non_power_of_two,GL_ARB_vertex_buffer_object,GL_ARB_vertex_program,GL_ARB_vertex_shader,GL_EXT_blend_equation_separate,GL_EXT_blend_func_separate,GL_EXT_blend_minmax,GL_EXT_blend_subtract,GL_EXT_copy_texture,GL_EXT_framebuffer_blit,GL_EXT_framebuffer_multisample,GL_EXT_framebuffer_object,GL_EXT_geometry_shader4,GL_EXT_packed_depth_stencil,GL_EXT_subtexture,GL_EXT_texture_array,GL_EXT_texture_object,GL_EXT_texture_sRGB,GL_EXT_vertex_array,GL_INGR_blend_func_separate,GL_KHR_debug,GL_NV_geometry_program4,GL_NV_vertex_program,GL_SGIS_texture_edge_clamp,GL_EXT_sRGB,GL_OES_blend_equation_separate,GL_OES_blend_func_separate,GL_OES_blend_subtract,GL_OES_depth24,GL_OES_depth32,GL_OES_framebuffer_object,GL_OES_packed_depth_stencil,GL_OES_single_precision,GL_OES_texture_npot,GLX_ARB_create_context,GLX_ARB_create_context_profile,GLX_ARB_framebuffer_sRGB,GLX_ARB_multisample,GLX_EXT_framebuffer_sRGB,GLX_EXT_swap_control,GLX_MESA_swap_control,GLX_SGIX_pbuffer,GLX_SGI_swap_control",

        "merge": False,
        "quiet": False,

        "alias": True,
        "headeronly": False,
        "loader": True,
        "mx": False,
        "mxglobal": False,
        "on_demand": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def _has_spec(self, spec):
        value = getattr(self.options, spec)
        return value != "None"

    def _get_spec_key(self, spec):
        if spec == "gl":
            return "{0}:{1}".format(spec, self.options.gl_profile)
        elif spec == "gles1":
            return "{0}:{1}".format(spec, "common")
        else:
            return spec
    
    def _get_spec_version(self, spec):
        return getattr(self.options, spec)
    

    def _get_api(self):
        api = ""
        for spec in ["egl", "gl", "gles1", "gles2", "glsc2", "glx", "vulkan", "wgl"]:
            if self._has_spec(spec):
                key = self._get_spec_key(spec)
                version = self._get_spec_version(spec)
                api = "{0};API;{1}={2}".format(api, key, version)
        return api.strip()

    def config_options(self):
        if self.options.mxglobal and not self.options.mx:
            raise ConanInvalidConfiguration("mxglobal option requires mx")
        if self.options.mx and self.options.on_demand:
            raise ConanInvalidConfiguration("mx option cannot be used together with on_demand")
        if self.options.mx and self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration("mx option cannot be used when buid_type is Debug")
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        
        if self._has_spec("wgl") and self.settings.os != "Windows":
            raise ConanInvalidConfiguration("API wgl {0} is not compatible"
                        " with {1}".format(self.options.wgl, self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-glad2" # + self.version
        os.rename(extracted_dir, self._source_subfolder)
        
    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["GLAD_API"] = self._get_api()
        cmake.definitions["GLAD_EXTENSIONS"] = "EXTENSIONS;{0}".format(self.options.extensions)
        
        cmake.definitions["GLAD_MERGE"] = self.options.merge
        cmake.definitions["GLAD_REPRODUCIBLE"] = True
        cmake.definitions["GLAD_QUIET"] = self.options.quiet

        cmake.definitions["GLAD_ALIAS"] = self.options.alias        
        cmake.definitions["GLAD_DEBUG"] = self.settings.build_type == "Debug"
        cmake.definitions["GLAD_HEADERONLY"] = self.options.headeronly
        cmake.definitions["GLAD_LOADER"] = self.options.loader
        cmake.definitions["GLAD_MX"] = self.options.mx
        cmake.definitions["GLAD_MXGLOBAL"] = self.options.mxglobal
        cmake.definitions["GLAD_ONDEMAND"] = self.options.on_demand
        
        cmake.definitions["GLAD_GENERATOR"] = "c" if self.settings.build_type == "Release" else "c-debug"
        cmake.definitions["GLAD_EXPORT"] = True
        cmake.definitions["GLAD_INSTALL"] = True
        
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        gen_glad_includes = "{}/gladsources/glad/include".format(self._build_subfolder)
        self.copy(pattern="*.h", dst="include", src=gen_glad_includes)
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")
        for spec in ["egl", "gl", "gles1", "gles2", "glsc2", "glx", "vulkan", "wgl"]:
            if self._has_spec(spec):
                self.cpp_info.defines.append("GLAD_HAS_{0}".format(str.upper(spec)))
