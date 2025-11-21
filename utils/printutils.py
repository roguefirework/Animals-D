from termcolor import colored

# Prints out an error message
def error(message : str) -> None:
    print(colored(f"[ERROR] {message}", 'red'))
# Prints out an info message
def info(message : str) -> None:
    print(colored(f"[INFO] {message}", 'blue'))
# Prints out a success message
def success(message : str) -> None:
    print(colored(f"[SUCCESS] {message}", 'green'))
# Prints out a warning message
def warning(message : str) -> None:
    print(colored(f"[WARNING] {message}", 'yellow'))
# Prints out a debug message
def debug(message : str) -> None:
    print(colored(f"[DEBUG] {message}", 'white'))
# Prints out a status message
def status(message : str) -> None:
    print(colored(f"[STATUS] {message}", 'cyan'))