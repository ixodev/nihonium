import sys
import argparse
from interpreter import Interpreter
import colorama

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Nihonium Interpreter, version 0.1.0")

    parser.add_argument("program",
                        nargs="?",
                        help="The file in which the program to run is located"
                        )

    parser.add_argument(
        "--shell",
        action="store_true",
        help="Start interactive shell instead of running a file"
    )

    parser.add_argument("--pretty-print-ast",
                        help="Print the generated AST without running the program",
                        action="store_true"
                        )

    parser.add_argument("--debug",
                        help="Switch to debug mode (not supported by VM mode)",
                        action="store_true"
                        )

    parser.add_argument("--vm",
                        help="Compile and launch with Nexcellence",
                        action="store_true"
                        )

    parser.add_argument("--natives",
                        help="Link to native Python modules",
                        type=str,
                        nargs="+",
                        default=[]
                        )

    parser.add_argument("--disable-default-natives",
                        help="Disable import of default native functions",
                        action="store_true")

    args = parser.parse_args()

    if not args.shell and args.program is None:
        parser.error("the following argument is required: program (unless --shell is used)")

    interpreter = Interpreter(args.program, args)
    result = None

    try:
        result = interpreter.run()
    except KeyboardInterrupt:
        print(colorama.Fore.BLUE, "\n\nExiting", colorama.Style.RESET_ALL)

    if result is None:
        result = 0

    print(f"\n{colorama.Fore.BLUE}Program exited with exit code {result}\n{colorama.Style.RESET_ALL}")
    sys.exit(result)