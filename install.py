import subprocess
import sys

# log_helper

INFO = 0
WARNING = 1
ERROR = 2
SUCCESS = 3

def log_user(level: int, *message, end="\n"):
    if level == INFO:
        print("\033[94m[INFO]:\033[0m", *message, end=end)
    elif level == WARNING:
        print("\033[93m[WARNING]:\033[0m", *message, end=end)
    elif level == ERROR:
        print("\033[91m[ERROR]:\033[0m", *message, end=end)
    elif level == SUCCESS:
        print("\033[92m[SUCCESS]:\033[0m", *message, end=end)
    else:
        print("\033[94m[INFO]:\033[0m", *message, end=end)

def install(package: str):
    log_user(INFO, f"Installing {package}")
    log_user(INFO, f"Running: \"{sys.executable} -m pip install {package}\"")
    log_user(INFO, "Proceed? (Y/n): ", end="")
    try:
        answer = input().lower()
    except EOFError:
        log_user(ERROR, "Unexpected EOF hit, aborting")
        sys.exit(1)
    if answer != "y":
        log_user(WARNING, "Rejected, aborting download")
        return subprocess.run('echo Abborting...', shell=True, stderr=subprocess.PIPE)
    
    log_user(INFO, "Installing... This may take a while...")
    
    return subprocess.run([sys.executable, '-m', 'pip', 'install', package], shell=True, stderr=subprocess.PIPE)

err = install("pyinstaller")
if err.returncode != 0:
    log_user(ERROR, "Failed to install pyinstaller")
    if err.stderr is not None:
        log_user(ERROR, err.stderr.decode("utf-8"))
    else:
        log_user(ERROR, "Could not get stderr from pip")
    sys.exit(1)
else:
    log_user(SUCCESS, "Successfully installed pyinstaller")

log_user(INFO, "Executing pyinstaller")
log_user(INFO, f"Running: \"{sys.executable} -m pyinstaller --onefile --distpath dist/bin --icon=assets/icon.ico klse.py\"")

log_user(INFO, "Proceed? (Y/n): ", end="")
try:
    answer = input().lower()
except EOFError:
    log_user(ERROR, "Unexpected EOF hit, aborting")
    sys.exit(1)

if answer != "y":
    log_user(INFO, "Rejected, aborting")
    sys.exit(0)

log_user(INFO, "Executing... This may take a while...")

err = subprocess.run([sys.executable, '-m', 'pyinstaller', '--onefile', '--distpath', 'dist/bin', '--icon=assets/icon.ico', 'klse.py'], shell=True, stderr=subprocess.PIPE)
if err.returncode != 0:
    log_user(ERROR, "Failed to execute pyinstaller, maybe due to anti-viruses such as avast, try running the following command separately:")
    log_user(ERROR, f"{sys.executable} -m pyinstaller --onefile --distpath dist/bin --icon=assets/icon.ico klse.py")
    log_user(ERROR, "If the above didn't work, you may try troubleshooting yourself by deleting it and reinstalling it manually")
    log_user(ERROR, f"  {sys.executable} -m pip install --no-cache --force-reinstall pyinstaller")

    if err.stderr is not None:
        log_user(ERROR, err.stderr.decode("utf-8"))
    else:
        log_user(ERROR, "Could not get stderr from pyinstaller")
    sys.exit(1)
else:
    log_user(SUCCESS, "Successfully executed pyinstaller")