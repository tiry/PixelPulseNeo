from typing import Any
import os
import psutil
import subprocess
import sys
import argparse
import logging


def get_cmd()->str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "../../../scripts/monitor.sh")
    absolute_path: str = os.path.abspath(relative_path)
    return f"{absolute_path}"

def get_git_cmd()->str:
    current_directory: str = os.path.dirname(os.path.realpath(__file__))
    relative_path: str = os.path.join(current_directory, "../../../")
    absolute_path: str = os.path.abspath(relative_path)
    
    return f"git -C {absolute_path} rev-parse HEAD"


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
        print(error_output)
        return (False, error_output)


def git_metrics() -> dict[str, Any]:
    
    metrics:dict[str, Any] = {}
    cmd:str = get_git_cmd()
    ok, data = execute_process(cmd)
    if ok:
        lines: list[str] = data.split("\n")
        metrics["git_rev"] = lines[0]
    else:
        print(f"ERROR {data}")
    return metrics
    
def system_metrics() -> dict[str, Any]:
    
    metrics:dict[str, Any] = {}
    ok, data = execute_process(get_cmd())
    if ok:
        lines: list[str] = data.split("\n")
        capture:bool = False
        for line in lines:
            if line == "BEGIN":
                capture=True
            elif line =="END":
                capture=False
            else:
                if capture:
                    parts: list[str] = line.split(":")
                    metrics[parts[0]] = parts[1]
    else:
        print(f"ERROR {data}")

    return metrics

def python_metrics() -> dict[str, Any]:
    metrics:dict[str, Any] = {}
    
    load1, load5, load15 = psutil.getloadavg()
 
    metrics["cpu_load1"] = round(load1,1)
    metrics["cpu_load5"] = round(load5,1)
    metrics["cpu_load15"] = round(load15,1)
    metrics["python_cpu"] = (load15/os.cpu_count()) * 100 #type: ignore

    return metrics

def all_metrics() -> dict[str, Any]:
    
    metrics: dict[str, Any] = system_metrics()
    p_metrics: dict[str, Any] = python_metrics()
    metrics.update(p_metrics)
    
    g_metrics: dict[str, Any] = git_metrics()
    metrics.update(g_metrics)
    
    return metrics

if __name__ == "__main__":
    res=all_metrics()
    for key in res.keys():
        print(f"{key}: {res[key]}")
        