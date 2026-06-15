 #!/usr/bin/env python3
  """Patch Mesa's getstring.c so GL_RENDERER / GL_VENDOR honor the
  MESA_RENDERER / MESA_VENDOR environment variables. Idempotent.

  Usage:  python patch_getstring.py <path-to-getstring.c>
  """
  import re
  import sys

  path = sys.argv[1] if len(sys.argv) > 1 else "mesa/src/mesa/main/getstring.c"
  src = open(path, encoding="utf-8").read()

  if "BEGIN MESA_RENDERER spoof override" in src:
      print("already patched")
      sys.exit(0)

  block = (
      "   /* --- BEGIN MESA_RENDERER spoof override --- */\n"
      "   {\n"
      "      const char *spoof_env = NULL;\n"
      "      switch (name) {\n"
      "      case GL_RENDERER: spoof_env = \"MESA_RENDERER\"; break;\n"
      "      case GL_VENDOR:   spoof_env = \"MESA_VENDOR\";   break;\n"
      "      default: break;\n"
      "      }\n"
      "      if (spoof_env != NULL) {\n"
      "         const char *spoof_val = getenv(spoof_env);\n"
      "         if (spoof_val != NULL && spoof_val[0] != '\\0')\n"
      "            return (const GLubyte *) spoof_val;\n"
      "      }\n"
      "   }\n"
      "   /* --- END MESA_RENDERER spoof override --- */\n"
  )

  fn = src.index("_mesa_GetString")
  m = re.search(r"switch\s*\(\s*name\s*\)", src[fn:])
  if not m:
      sys.exit("could not find 'switch (name)' inside _mesa_GetString")
  ins = fn + m.start()
  line_start = src.rfind("\n", 0, ins) + 1
  src = src[:line_start] + block + src[line_start:]

  if not re.search(r"(?m)^\s*#\s*include\s*<stdlib\.h>", src):
      inc = src.index("#include")
      ls = src.rfind("\n", 0, inc) + 1
      src = src[:ls] + "#include <stdlib.h>\n" + src[ls:]

  open(path, "w", encoding="utf-8").write(src)
  print("patched OK")
