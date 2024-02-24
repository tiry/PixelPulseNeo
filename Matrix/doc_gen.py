import argparse
import os
from typing import Any
import datetime
from Matrix.driver.executor import CommandExecutor
from Matrix.driver.commands.base import TEST_ONLY_COMMANDS

def document_commands(cmdlist: list[dict[str, Any]]):
    lines = []

    lines.append("# Commands")

    for cmd in cmdlist:
        if cmd["name"] in TEST_ONLY_COMMANDS:
            continue
        print(cmd)
        lines.append(f'\n## {cmd["name"]}')

        lines.append(f'\n{cmd["description"]}')

        folder = os.path.dirname(os.path.realpath(__file__))
        ReadMePath = f"{folder}/driver/commands/{cmd['name']}/ReadMe.md"
        if os.path.exists(ReadMePath):
            lines.append(
                f'\n\nMore details and configuration, see [{cmd["name"]}/ReadMe.md]({cmd["name"]}/ReadMe.md)'
            )

        for screenshot in cmd["screenshots"]:
            lines.append(f'\n<img src="screenshots/{screenshot}"/>')

    return "\n".join(lines)


if __name__ == "__main__":
    ###################################
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    executor = CommandExecutor(schedule_file=None)
    cmds: list[dict[str, Any]] = executor.get_commands()
    ReadMeContent = document_commands(cmds)

    # add gen
    # cmd_line = ' '.join(sys.argv)
    cmd_line = "python -m Matrix.doc_gen"

    generated = f"Automatically generated using `{cmd_line}` on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}."

    ReadMeContent += f"\n<br/><hr/>\n\n{generated}"

    folder = os.path.dirname(os.path.realpath(__file__))
    ReadMePath = f"{folder}/driver/commands/ReadMe.md"

    with open(ReadMePath, "w", encoding="utf-8") as file:
        file.write(ReadMeContent)

    executor.stop()
