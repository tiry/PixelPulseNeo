import subprocess

def execute_process(cmd_line:str) -> tuple[bool, str]:
    
    # Start the process
    shell_process = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to complete and read stdout and stderr
    stdout, stderr = shell_process.communicate()

    # Decode the output from bytes to string if necessary (Python 3)
    output: str = stdout.decode()
    error_output: str = stderr.decode()

    # Check if the process has any errors
    if shell_process.returncode == 0:
        return (True, output)
    else:
        print("Process completed with errors. Error Output:")
        print(f"stderr: {error_output}")
        print(f"stdout: {output}")
        return (False, error_output)

