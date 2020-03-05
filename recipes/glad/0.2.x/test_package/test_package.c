#ifdef GLAD_HAS_EGL
#include <glad/egl.h>
#endif

#ifdef GLAD_HAS_GL
#include <glad/gl.h>
#endif

#if 0
#ifdef GLAD_HAS_GLES1
#include <glad/gles1.h>
#endif
#endif

#ifdef GLAD_HAS_GLES2
#include <glad/gles2.h>
#endif

#ifdef GLAD_HAS_GLSC2
#include <glad/glsc2.h>
#endif

#ifdef GLAD_HAS_GLX
#include <glad/glx.h>
#endif

#ifdef GLAD_HAS_VULKAN
#include <glad/vulkan.h>
#endif

#ifdef GLAD_HAS_WGL
#include <glad/wgl.h>
#endif

#include <stdlib.h>

int main() {
  return EXIT_SUCCESS;
}
