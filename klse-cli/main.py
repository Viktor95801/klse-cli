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

# klse-cli
from options import *

# const

if os.name == "nt":
    OS = "windows"
else:
    OS = "posix"

# default commands
default_search_path = ""

default_options = {
    "-tp": Opt("tp", "Set the tasks path to search for klse.json `klse -tp=\"my/path/to/klse/json/file\" task`"),
}

default_commands = {
    "help": Command("help", "Show this help message"),
    "task": Command("task", "Execute a klse.json tasks file `klse -tp dir task \"build release\"`"),
    "build-dir": Command("build-dir", "Prepares all the bin and build directories based on your current CD directory")
}

def prepare_commands():
    # Opt
    def task_path_klse(new_path: str):
        global default_search_path
        default_search_path = new_path
    # Commands
    
    #TODO: Improve the logic on this
    def task_exec_klse(task_sequence: str):
        task_sequence: list[str] = task_sequence.strip().split(" ")
        print()
        if task_sequence[0] == '':
            print("No task provided")
            sys.exit(1)
        path = os.path.join(default_search_path, "klse.json")
        if os.path.isfile(path):
            with open(path) as f:
                kf: dict = json.loads(f.read())
        else:
            print(f"Could not find or load file `{path}`")
            sys.exit(1)
            
        kf = kf.get("task", None)
        if kf is None:
            print(f"Could not find a \"task\" object on file `{path}`")
            sys.exit(1)
        
        def exec_task(task: dict):
            if OS in task.keys():
                subprocess.run(task[OS], shell=True)
            elif "task" in task.keys():
                subprocess.run(task["task"], shell=True)
            else:
                print("\033[91mERROR: Invalid Task!!!\033[0m")
                sys.exit(1)
        
        if task_sequence[0] in kf.keys():
            kf = kf[task_sequence[0]]
            task_sequence.pop(0)
        while len(task_sequence) > 0:
            if "childs" in kf.keys() and task_sequence[0] in kf["childs"].keys():
                kf = kf["childs"][task_sequence[0]]
                task_sequence.pop(0)
            else:
                break
            
        exec_task(kf)
        # if to_exec[0] in klse["task"].keys():
        #     if OS in klse["task"][to_exec[0]].keys():
        #         subprocess.run(klse["task"][to_exec[0]][OS], shell=True)
        #     if len(to_exec) > 1:
        #         if to_exec[1] in klse["task"][to_exec[0]]["childs"]:
        #             if OS in klse["task"][to_exec[0]]["childs"][to_exec[1]]:
        #                 subprocess.run(klse["task"][to_exec[0]]["childs"][to_exec[1]][OS], shell=True)
        #         else:
        #             print(f"Subtask `{to_exec[1]}` was not found")
        #             sys.exit(1)
        # else:
        #     print(f"The task `{to_exec[0]}` was not found.")
        #     sys.exit(1)
        
    def help_klse():
        print("Usage: klse-cli [options] [command]\n")
        
        cmm: list[Command] = [c for c in default_commands.values() if isinstance(c, Command)]
        opt: list[Opt] = [o for o in default_options.values() if isinstance(o, Opt)]
        
        print("Main commands:")
        for c in cmm:
            print(f"\t{c.name} - {c.description}")
        print("Options:")
        for o in opt:
            print(f"\t-{o.opt} - {o.description}")
    def build_dir_klse():
        directory: str = os.path.join(os.getcwd(), "build") 
        if not os.path.exists(directory):
            os.mkdir(directory)
        
        for path in ["/libs", "/bin", "/obj"]:
            pth = directory + path
            
            if not os.path.exists(pth):
                os.mkdir(pth)
        
    
    default_options["-tp"].setExec(task_path_klse)
    
    default_commands["help"].setExec(help_klse)
    default_commands["task"].setExec(task_exec_klse) 
    default_commands["build-dir"].setExec(build_dir_klse)

def lex_parse(args: list[str]) -> tuple[Command, list[Opt], list[str]]:
    opts = []
    cmm = None
    cmm_set = False
    arguments = []

    for i, arg in enumerate(args):
        if arg.startswith('-'):
            arg = arg[1:]
            if arg.startswith("tp"):
                opts.append(default_options["-tp"])
                if "=" in arg:
                    arg = arg.split("=")
                    print(arg[1])
                    arguments.append(arg[1])
                else:
                    print(f"Expected '=<path>' at end of '-{arg}' but didn't get it.")
                    sys.exit(1)
            else:
                print(f"Unknown option '-{arg}', use `klse-cli help` to get help")
                sys.exit(1)
        else:
            match arg:
                case "help":
                    cmm = default_commands["help"]
                    cmm_set = True
                case "build-dir":
                    cmm = default_commands["build-dir"]
                    cmm_set = True
                case "task":
                    cmm = default_commands["task"]
                    to_append: list[str] = []
                    for arg2 in args[i + 1:]:
                        to_append.append(arg2)
                    arguments.append(" ".join(to_append))

                    break
                    cmm_set = True
                case _:
                    print(f"Unknown command '{arg}', use `klse-cli help` to get help")
    
    return cmm, opts, arguments

def interpret_cmd(command: Command, options: list[Opt], arguments: list[str]):
    global default_options, default_commands, default_search_path
    
    for opt in options:
        if opt == default_options["-tp"]:
            if arguments:
                opt.exec(arguments.pop(0))
            else:
                print("Arguments list is empty, this means the CLI tool expected an argument for an option but it was missing")
                sys.exit(1)
    if command:
        if command == default_commands["task"]:
            if arguments:
                command.exec(arguments.pop(0))
            else:
                print("Arguments list is empty, this means the CLI tool expected an argument for an option but it was missing")
                sys.exit(1)
        else:
            command.exec()

# compilers = [shutil.which("cc"), shutil.which("c++")]
# if not compilers[0]:
#     print("Couldn't find the C compiler (assumes 'cc' alias), please create an alias for your C compiler or download one from the internet (w64devkit/mingw or gcc)")
#     sys.exit(1)
# if not compilers[1]:
#     print("Couldn't find the C++ compiler (assumes 'c++' alias), please create an alias for your C compiler or download one from the internet (w64devkit/mingw or gcc)")

def main(args: list[str] = sys.argv):
    prepare_commands()
    if len(args) == 0:
        print("Use `klse-cli help` to get help")
        sys.exit(0)
    command, options, arguments = lex_parse(args)
    
    interpret_cmd(command, options, arguments)

    print("\nENDED EXECUTION")
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
    sys.exit(0)