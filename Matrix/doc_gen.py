import argparse
import os, sys
from Matrix.driver.executor import CommandExecutor
import datetime

def document_commands(cmds):

    lines = []

    lines.append("# Commands")

    for cmd in cmds:
        print(cmd)
        lines.append(f'\n## {cmd["name"]}')
        
        lines.append(f'\n{cmd["description"]}')

        for screenshot in cmd["screenshots"]:
            lines.append(f'\n<img src="screenshots/{screenshot}"/>')

    return "\n".join(lines)


if __name__ == "__main__":

    ###################################
    parser = argparse.ArgumentParser()   
    args = parser.parse_args()
    
    executor = CommandExecutor(schedule_file=None)    
    cmds = executor.get_commands()
    ReadMeContent = document_commands(cmds)

    # add gen
    # cmd_line = ' '.join(sys.argv)
    cmd_line = "python -m Matrix.doc_gen"

    generated = f"Automatically generated using `{cmd_line}` on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}."

    ReadMeContent += f"\n<br/><hr/>\n\n{generated}"

    folder = os.path.dirname(os.path.realpath(__file__))
    ReadMePath = f"{folder}/driver/commands/ReadMe.md"

    with open(ReadMePath, 'w') as file:
        file.write(ReadMeContent)

    executor.stop()
    
    