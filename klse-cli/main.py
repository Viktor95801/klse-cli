# system
import sys
import os
import subprocess
from typing import Union

# klse-cli
from options import *

# default commands

default_search_path = "."

default_options = {
    "-tp": Opt("tp", "Set the tasks path to search for klse.json `klse -tp=\"my/path/to/klse/json/file\" task`"),
}

default_commands = {
    "help": Command("help", "Show this help message"),
    "task": Command("task", "Execute a klse.json tasks file"),
}

def prepare_commands():
    # Opt
    def task_path_klse(new_path: str):
        default_search_path = new_path
    # Commands
    def task_exec_klse():
        raise NotImplementedError
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
    
    default_options["-tp"].setExec(task_path_klse)
    
    default_commands["help"].setExec(help_klse)
    default_commands["task"].setExec(task_exec_klse) 




def lex_parse(args: list[str]) -> tuple[Command, list[Opt], list[str]]:
    opts = []
    cmm = None
    cmm_set = False
    arguments = []

    for arg in args:
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
            if cmm_set:
                print("Only one command per `klse-cli` usage")
            match arg:
                case "help":
                    cmm = default_commands["help"]
                    cmm_set = True
                case "task":
                    cmm = default_commands["task"]
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
        command.exec()

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