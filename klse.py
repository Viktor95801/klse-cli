# Copyright (c) 2025 Kaklik And Viktor Hugo Caetano M. Goulart

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# system
import json
import sys
import os
import subprocess
import shutil
from typing import Union
import argparse

# logging helper

INFO = 0
WARNING = 1
ERROR = 2
SUCCESS = 3

def log_user(level: int, *message):
    if level == INFO:
        print("\033[94m[INFO]:\033[0m", *message)
    elif level == WARNING:
        print("\033[93m[WARNING]:\033[0m", *message)
    elif level == ERROR:
        print("\033[91m[ERROR]:\033[0m", *message)
    elif level == SUCCESS:
        print("\033[92m[SUCCESS]:\033[0m", *message)

# const

OS = "windows" if os.name == "nt" else "posix"

def find_compiler(compiler_names: list[str]) -> Union[str, None]:
    for compiler in compiler_names:
        if shutil.which(compiler):
            return compiler
    return None

compilers = {
    "cc": shutil.which("cc"),
    "c++": shutil.which("c++")
}

if not compilers["cc"]:
    compilers["cc"] = find_compiler([
        "gcc",
        "clang",
        "tcc",
        "icc",
        "pgcc",
        "sdcc",
        "armcc",
        "iccarm"
    ])
    if compilers["cc"] is None:
        log_user(ERROR, "Couldn't find the C compiler (assumes 'cc' alias), please create an alias for your C compiler or download one from the internet (mingw or gcc)")
        sys.exit(1)
if not compilers["c++"]:
    compilers["c++"] = find_compiler([
        "g++",
        "clang++",
        "icpc",
        "pgcpp",
        "armcc",
        "iccarm"
    ])
    if compilers["c++"] is None:
        log_user(ERROR, "Couldn't find the C++ compiler (assumes 'c++' alias), please create an alias for your C++ compiler or download one from the internet (mingw or gcc)")
        sys.exit(1)
del find_compiler

parser = argparse.ArgumentParser(
    prog="KLSE",
    usage="klse [options] [command] <arguments>",
    epilog="Copyright (c) 2025 Kaklik And Viktor Hugo Caetano M. Goulart",
    prefix_chars="-",
    add_help=False,
    exit_on_error=False
)

# program

# handles

def handle_build_dir(directory: str):
    if directory is None:
        directory = os.getcwd()
    directory = os.path.join(directory, "dist")
    if not os.path.exists(directory):
        os.mkdir(directory)
    
    for p in ["libs", "bin", "obj"]:
        path: str = os.path.join(directory, p)
        if not os.path.exists(path):
            os.mkdir(path)

def handle_task(task_path, task_sequence):
    if len(task_sequence) == 0:
        log_user(ERROR, "No task provided")
        sys.exit(1)
    path = os.path.join(task_path, "klse.json")
    if os.path.isfile(path):
        with open(path) as f:
            try:
                kf: dict = json.loads(f.read())
            except json.JSONDecodeError:
                log_user(ERROR, f"Could not load file `{path}` (probably due to invalid json)")
                sys.exit(1)
    else:
        log_user(ERROR, f"Could not find or load file `{path}`")
        sys.exit(1)
    
    kf = kf.get("task", None)
    if kf is None:
        log_user(ERROR, f"Could not find a \"task\" object on file `{path}`")
        sys.exit(1)
    
    def exec_task(task: dict):
        if OS in task.keys():
            subprocess.run(task[OS], shell=True)
        elif "task" in task.keys():
            subprocess.run(task["task"], shell=True)
        else:
            log_user(ERROR, f"Invalid task on file `{path}` (maybe due to incompatibility with your OS)")
            sys.exit(1)

    if task_sequence[0] in kf.keys():
        kf = kf[task_sequence[0]]
        task_sequence.pop(0)
    else:
        log_user(ERROR, f"Could not find task `{task_sequence[0]}` on file `{path}`")
        sys.exit(1)
    while len(task_sequence) > 0:
        if "childs" in kf.keys() and task_sequence[0] in kf["childs"].keys():
            kf = kf["childs"][task_sequence[0]]
            task_sequence.pop(0)
        else:
            break
    
    exec_task(kf)

def handle_smart_compile(language: str, file_path: str, output_dir: str, CFLAGS: list[str]):
    if file_path is None:
        log_user(ERROR, "Cannot compile unknown file")
        sys.exit(1)
    if language is None:
        log_user(ERROR, f"Cannot compile {file_path} when it's language is unknown")
        sys.exit(1)
    if output_dir is None:
        output_dir = os.getcwd()
    if CFLAGS is None:
        CFLAGS = []
    CFLAGS: str = " ".join(CFLAGS)
    
    if language == "c":
        compiler = compilers["cc"]
    elif language == "c++":
        compiler = compilers["c++"]
    else:
        log_user(ERROR, f"Cannot compile {file_path} for language {language}")
        sys.exit(1)
    
    if not os.path.isfile(file_path):
        log_user(ERROR, f"Cannot compile {file_path} because it doesn't exist or it is not a file")
        sys.exit(1)
    
    if os.path.exists(output_dir):
        if not os.path.isdir(output_dir):
            log_user(ERROR, f"Cannot use {output_dir} as output directory because it doesn't exist or it is not a directory")
            sys.exit(1)
    else:
        os.mkdir(output_dir)
    
    cache_file = os.path.join(output_dir, "klse_CFLAGS.json.cache")
    if os.path.isfile(cache_file):
        with open(cache_file) as f:
            try:
                cache: dict = json.load(f)
            except json.JSONDecodeError:
                log_user(ERROR, f"Could not load cache file `{cache_file}` (probably due to invalid json)")
                sys.exit(1)
    else:
        cache = {}
    
    update_CFLAGS = False
    if file_path in cache.keys():
        if cache[file_path] != CFLAGS:
            update_CFLAGS = True
            log_user(WARNING, f"File {file_path} is already compiled with different CFLAGS (\"{cache[file_path]}\" != \"{CFLAGS}\"), recompiling...")
            cache[file_path] = CFLAGS
            with open(cache_file, "w") as f:
                json.dump(cache, f)
    else:
        cache[file_path] = CFLAGS
        update_CFLAGS = True
        with open(cache_file, "w") as f:
            json.dump(cache, f)
    out_file = f"{output_dir}/{os.path.splitext(os.path.basename(file_path))[0]}.o"
    
    command = f"{compiler} {CFLAGS} -c {file_path} -o {out_file}"
    
    src_mtime = os.path.getmtime(file_path)
    out_mtime = os.path.getmtime(out_file) if os.path.isfile(out_file) else 0
    if not os.path.exists(out_file) or src_mtime > out_mtime or update_CFLAGS:
        log_user(SUCCESS, f"Running: {command}")
        err = subprocess.run(command, stderr=subprocess.PIPE)
        if err.returncode != 0:
            log_user(ERROR, f"Compilation failed with error code {err.returncode}")
            log_user(ERROR, err.stderr.decode("utf-8"))
            sys.exit(1)
    else:
        log_user(SUCCESS, f"{out_file} is up to date")

def handle_compile_folder(language: str, folder_path: str, output_dir: str, CFLAGS: list[str], recursive: bool):
    if folder_path is None:
        log_user(ERROR, "Cannot compile unknown file")
        sys.exit(1)
    if language is None:
        log_user(ERROR, f"Cannot compile {file_path} when it's language is unknown")
        sys.exit(1)
    if output_dir is None:
        output_dir = os.getcwd()
    if CFLAGS is None:
        CFLAGS = []
    
    if not os.path.isdir(folder_path):
        log_user(ERROR, f"Cannot compile {folder_path} because it doesn't exist or it is not a directory")
        sys.exit(1)
    
    for file in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file)):
            handle_smart_compile(language, os.path.join(folder_path, file), output_dir, CFLAGS)
        elif os.path.isdir(os.path.join(folder_path, file)) and recursive:
            handle_compile_folder(language, os.path.join(folder_path, file), os.path.join(output_dir, file), CFLAGS, recursive)
    
# Command stuff
subparsers = parser.add_subparsers(dest='command', title='Commands')

# Options
opt_group = parser.add_argument_group('Options')

opt_group.add_argument('-tp', '--task-path', default='.', help='Path to the directory containing `klse.json` file')
opt_group.add_argument('-r', '--recursive', action='store_true', help='Recursively executes said command')

# Subcommand parser
help_parser = subparsers.add_parser('help', help='Show this help message, you can pass in a command to get more detailed help')
help_parser.add_argument('help_command', nargs='?', help='The command you want more detailed help for')
detailed_help: dict[str, str] = {
    'help': """
    Show a help message.
    Use `klse help <command>` to get more detailed help for a command.
""",
    'task': """
    Execute task operations.
    It searches for a file named `klse.json` in the current directory or in the specified directory.
    If it doesn't find it, it exits with error.
    You can specify a directory by using `-tp` or `--task-path`, such as:
        `klse -tp /path/to/dir task build release`
""",
    'build-dir': """
    Prepares bin, obj and libs in a dist directory.
    You can specify a directory by passing it in as an optional argument, such as:
        `klse build-dir /path/to/dir`
    Else it just assumes the current working directory.
""",
    'smart-compile': """
    Compiles just modified files from the specified directory and puts the result in the specified directory.
    You can specify a directory by passing it in as an optional argument, such as:
        `klse smart-compile c hello.c path/to/dir`
    Else it just assumes the current working directory.
    You can specify CFLAGS by passing it in as an optional argument, such as:
        `klse smart-compile c hello.c . -- -O3 -Wall`
    Else it just assumes no CFLAGS (you need the `--` before the CFLAGS, else the parser just assumes the cflags are options and it is gonna give you an error).
""",
    'compile-folder': """
    Compiles just modified files from the specified directory and puts the result in the specified directory.
    You can specify a directory by passing it in as an optional argument, such as:
        `klse compile-folder c /path/to/dir path/to/dir2`
    Else it just assumes the current working directory.
    You can specify CFLAGS by passing it in as an optional argument, such as:
        `klse compile-folder c /path/to/dir path/to/dir2 -- -O3 -Wall`
    Else it just assumes no CFLAGS (you need the `--` before the CFLAGS, else the parser just assumes the cflags are options and it is gonna give you an error).
    
    If you want to recursively compile a folder, use the `-r` or `--recursive` flag, such as:
        `klse -r compile-folder c /path/to/dir path/to/dir2 -- -O3 -Wall`
    """
}

task_parser = subparsers.add_parser('task', help='Execute task operations')
task_parser.add_argument('task_args', nargs='*', help='Arguments for the task command')

build_dir_parser = subparsers.add_parser('build-dir', help='Prepares all the bin and build directories')
build_dir_parser.add_argument('directory', nargs='?', help='Directory to prepare')

smart_compile_parser = subparsers.add_parser('smart-compile', help='Compiles just modified files from the specified directory and puts the result in the specified directory')
smart_compile_parser.add_argument('language', nargs=1, help='The language (c/c++) to compile')
smart_compile_parser.add_argument('file_path', nargs=1, help='The path to the file to compile')
smart_compile_parser.add_argument('output_dir', nargs='?', help='The path to the output directory')
smart_compile_parser.add_argument('CFLAGS', nargs='*', help='The CFLAGS to use (pass it after `--` so the parser doesn\' interpret it as options and instead interpret it as arguments such as `klse smart-compile c hello.c . -- -O3`)')

compile_folder_parser = subparsers.add_parser('compile-folder', help='Compiles just modified files from the specified directory and puts the result in the specified directory')
compile_folder_parser.add_argument('language', nargs=1, help='The language (c/c++) to compile')
compile_folder_parser.add_argument('directory', nargs=1, help='The directory to compile')
compile_folder_parser.add_argument('output_dir', nargs='?', help='The path to the output directory')
compile_folder_parser.add_argument('CFLAGS', nargs='*', help='The CFLAGS to use (pass it after `--` so the parser doesn\' interpret it as options and instead interpret it as arguments such as `klse smart-compile c hello.c . -- -O3`)')

# main

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    log_user(ERROR, "Invalid arguments/options/command\n")
    parser.print_help()
    print();log_user(ERROR, "Aborting...")
    sys.exit(1)

match args.command:
    case 'task':
        handle_task(args.task_path, args.task_args)
    case 'help':
        if args.help_command is not None:
            if args.help_command in detailed_help.keys():
                print(detailed_help[args.help_command])
            else:
                log_user(WARNING, f"Unknown command: {args.help_command}")
        else:
            parser.print_help()
    case 'build-dir':
        handle_build_dir(args.directory)
    case 'smart-compile':
        handle_smart_compile(args.language, args.file_path, args.output_dir, args.CFLAGS)
    case 'compile-folder':
        handle_compile_folder(args.language, args.directory, args.output_dir, args.CFLAGS, args.recursive)
    case _:
        parser.print_help() 
