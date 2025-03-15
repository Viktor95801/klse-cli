import os

exe_suffix = ''
if os.name == "nt":
    exe_suffix = ".exe"

def add_suffix(string1, string2):
    return string1 + string2

# Get the PATH variable
path_variable = os.environ["PATH"]

# Split the PATH variable into individual directories
directories = path_variable.split(os.pathsep)

# Define a list of common C compiler names
c_compilers = [
    add_suffix("gcc", exe_suffix),
    add_suffix("clang", exe_suffix),
    add_suffix("cc", exe_suffix),
    add_suffix("tcc", exe_suffix)
]

# Search for C compilers in the PATH variable
for directory in directories:
    for compiler in c_compilers:
        compiler_path = os.path.join(directory, compiler)
        if os.path.exists(compiler_path) and os.access(compiler_path, os.X_OK):
            print(f"Found C compiler: {compiler_path}")