import sys

from dotenv import load_dotenv

COMMANDS = {
    "basic-eval": "strands_investig.basic_eval",
    "experiment-generation": "strands_investig.experiment_generation",
    "decider": "strands_investig.decider",
    "download-decider": "strands_investig.download_decider",
    "clean": "strands_investig.clean",
}


def main() -> None:
    load_dotenv()

    if sys.platform == "win32":
        # Rich prints unicode (e.g. emoji) that the legacy Windows console
        # codepage can't encode; force utf-8 on the output streams.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        available = ", ".join(COMMANDS)
        print(f"Usage: strands-investig <command>\nAvailable commands: {available}")
        sys.exit(1)

    import importlib

    module = importlib.import_module(COMMANDS[sys.argv[1]])
    module.run()
