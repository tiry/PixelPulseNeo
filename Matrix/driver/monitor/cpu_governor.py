import argparse
from  Matrix.driver.monitor.base  import execute_process

POWER_SAVE_MODE:str = "powersave"
NORMAL_MODE:str = "ondemand"

def get_frequency_governor() -> str | None:
     ok, data = execute_process("cpufreq-info -p")
     if ok is True:
         return data
     else:
         return None

def set_cpu_mode(mode:str) -> str | None:
     ok, data = execute_process(f"cpufreq-set governor -g {mode}")
     if ok is True:
         return data
     else:
         return None

def set_cpu_sleep_mode() -> str | None:
    return set_cpu_mode(POWER_SAVE_MODE)

def set_cpu_normal_mode() -> str | None:
    return set_cpu_mode(NORMAL_MODE)


if __name__ == "__main__":

    ###################################
    # act as a simple CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep", help="enable power save mode", action="store_true")
    parser.add_argument("--wakeup",  help="disable power save mode", action="store_true")

    args = parser.parse_args()

    if args.sleep:
        set_cpu_normal_mode()
    if args.wakeup:
        set_cpu_normal_mode()
    
    print(f" Current CPU Settings {get_frequency_governor()}")
